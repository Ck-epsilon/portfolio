# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Scraper Dashboard Backend — FastAPI API + WebSocket proxy for Scrapyd.

Provides:
- POST /jobs — schedule a new scrape job via Scrapyd
- GET /jobs — list all jobs and their status
- GET /jobs/{job_id} — get single job status + results
- WS /ws/{job_id} — live log streaming (proxied from Scrapyd logs)
- GET /jobs/{job_id}/export — download results as CSV/JSON
- GET /health — service health check
"""

import asyncio
import csv
import glob as _glob
import io
import json
import logging
import os
import re as _re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
import yaml
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────
SCRAPYD_URL: str = os.getenv("SCRAPYD_URL", "http://scrapyd:6800")
SCRAPYD_PROJECT: str = os.getenv("SCRAPYD_PROJECT", "scraper_stack")
CONFIGS_DIR: str = os.getenv("CONFIGS_DIR", "/app/configs")
RESULTS_DIR: str = os.getenv("RESULTS_DIR", "/app/output")

# ── App ────────────────────────────────────────────────────────
app = FastAPI(
    title="Scraper Stack Dashboard",
    version="2.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Scrapyd Client ─────────────────────────────────────────────

class ScrapydClient:
    """HTTP client for Scrapyd's JSON API."""

    def __init__(self, base_url: str = SCRAPYD_URL):
        self.base_url = base_url.rstrip("/")

    async def _post(self, endpoint: str, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                urljoin(self.base_url + "/", endpoint),
                data=data,
            )
            resp.raise_for_status()
            return resp.json()

    async def _get(self, endpoint: str) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(urljoin(self.base_url + "/", endpoint))
            resp.raise_for_status()
            return resp.json()

    async def schedule(self, spider: str, config_name: str, **kwargs) -> dict:
        """Schedule a spider run. Returns Scrapyd job ID."""
        return await self._post("schedule.json", {
            "project": SCRAPYD_PROJECT,
            "spider": spider,
            "setting": [
                f"CONFIG_NAME={config_name}",
                f"FEED_URI={RESULTS_DIR}/{config_name}_%(time)s.json",
                "FEED_FORMAT=json",
            ],
            **kwargs,
        })

    async def list_jobs(self) -> dict:
        return await self._get("listjobs.json?project=" + SCRAPYD_PROJECT)

    async def cancel(self, job_id: str) -> dict:
        return await self._post("cancel.json", {
            "project": SCRAPYD_PROJECT,
            "job": job_id,
        })

    async def job_status(self, job_id: str) -> dict:
        jobs = await self.list_jobs()
        for state in ("pending", "running", "finished"):
            for job in jobs.get(state, []):
                if job.get("id") == job_id:
                    return {"id": job_id, "status": state, **job}
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    async def stream_logs(self, job_id: str, ws: WebSocket):
        """Poll Scrapyd logs and stream to WebSocket client."""
        log_url = urljoin(
            self.base_url + "/",
            f"logs/{SCRAPYD_PROJECT}/{job_id}/{job_id}.log",
        )
        last_size = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                try:
                    resp = await client.get(log_url)
                    if resp.status_code == 200:
                        content = resp.text
                        if len(content) > last_size:
                            new_lines = content[last_size:]
                            last_size = len(content)
                            for line in new_lines.strip().split("\n"):
                                line = line.strip()
                                if line:
                                    await ws.send_json(_parse_log_line(line))
                    await asyncio.sleep(1.0)
                except WebSocketDisconnect:
                    break
                except Exception:
                    await asyncio.sleep(2.0)


def _parse_log_line(line: str) -> dict[str, str]:
    """Parse a Scrapy log line into a structured log event."""
    if "ERROR" in line:
        level = "error"
    elif "WARNING" in line:
        level = "warn"
    elif "DEBUG" in line:
        level = "debug"
    else:
        level = "info"
    return {"type": "log", "level": level, "message": line}


scrapyd = ScrapydClient()

# Job ID → config_name mapping (Scrapyd doesn't return spider args in job status)
_job_configs: dict[str, str] = {}

# ── CSV Injection Guard ────────────────────────────────────────

_CSV_DANGER_RE = _re.compile(r"^[=+\-@\t\r]")


def _sanitize_csv(value: str) -> str:
    """Prefix cells starting with =, +, -, @, tab, CR to prevent CSV injection."""
    if not value:
        return value
    if _CSV_DANGER_RE.match(value):
        return "'" + value
    return value

# ── REST Endpoints ─────────────────────────────────────────────

@app.get("/health")
async def health() -> dict:
    """Health check — verifies Scrapyd is reachable."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(urljoin(SCRAPYD_URL, "daemonstatus.json"))
            scrapyd_ok = resp.status_code == 200
    except Exception:
        scrapyd_ok = False
    return {
        "status": "ok" if scrapyd_ok else "degraded",
        "scrapyd": "reachable" if scrapyd_ok else "unreachable",
    }


@app.get("/configs")
async def list_configs():
    """List available scraper config YAML files."""
    config_dir = Path(CONFIGS_DIR)
    if not config_dir.exists():
        return {"configs": []}
    configs = []
    for f in sorted(config_dir.glob("*.yaml")):
        try:
            cfg = yaml.safe_load(f.read_text(encoding="utf-8"))
            configs.append({
                "name": f.stem,
                "display": cfg.get("name", f.stem),
                "start_urls": cfg.get("start_urls", []),
                "fields": list(cfg.get("selectors", {}).keys()),
            })
        except Exception:
            logger.exception("Failed to parse config %s", f)
            configs.append({"name": f.stem, "error": "Invalid YAML"})
    return {"configs": configs}


@app.post("/jobs")
async def create_job(body: dict[str, Any]):
    """Schedule a new scrape job.

    Request body::

        {"config": "hackernews", "spider": "generic"}
    """
    config_name = body.get("config", "")
    if not config_name:
        raise HTTPException(status_code=400, detail="config is required")

    config_path = Path(CONFIGS_DIR) / f"{config_name}.yaml"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail=f"Config '{config_name}' not found")

    spider = body.get("spider", "generic")
    result = await scrapyd.schedule(spider, config_name)
    job_id = result.get("jobid", "")
    if job_id:
        _job_configs[job_id] = config_name  # Map job_id → config_name for export

    return {
        "job_id": job_id,
        "status": "pending",
        "config": config_name,
        "spider": spider,
    }


@app.get("/jobs")
async def list_jobs():
    """List all jobs grouped by status."""
    return await scrapyd.list_jobs()


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get a single job's status and metadata."""
    return await scrapyd.job_status(job_id)


@app.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running or pending job."""
    return await scrapyd.cancel(job_id)


@app.get("/jobs/{job_id}/export")
async def export_job(
    job_id: str,
    export_format: str = "csv",
) -> Any:
    """Download job results. Matches Scrapyd FEED_URI pattern."""
    config_name = _job_configs.get(job_id)
    if not config_name:
        raise HTTPException(status_code=404, detail="Job not found or config unknown")

    # Scrapyd writes: {config_name}_{timestamp}.json
    pattern = str(Path(RESULTS_DIR) / f"{config_name}_*.json")
    matches = sorted(_glob.glob(pattern), reverse=True)
    if not matches:
        raise HTTPException(status_code=404, detail="Results file not found")

    results_path = Path(matches[0])
    if not results_path.exists():
        raise HTTPException(status_code=404, detail="Results not found")

    items = json.loads(results_path.read_text(encoding="utf-8"))

    if export_format == "json":
        return items

    # CSV export
    if not items:
        return StreamingResponse(iter(["No data"]), media_type="text/csv")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(items[0].keys()))
    writer.writeheader()
    for item in items:
        writer.writerow({k: _sanitize_csv(str(v)) for k, v in item.items()})

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={job_id}.csv"},
    )


@app.websocket("/ws/{job_id}")
async def stream_job_logs(ws: WebSocket, job_id: str):
    """WebSocket endpoint — streams live Scrapyd logs."""
    await ws.accept()
    await scrapyd.stream_logs(job_id, ws)


@app.get("/")
async def root():
    return {
        "service": "Scraper Stack Dashboard",
        "version": "2.0.0",
        "docs": "/docs",
    }
