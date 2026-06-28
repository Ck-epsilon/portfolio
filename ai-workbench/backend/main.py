# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""AI Workbench Backend — CrewAI-powered multi-agent research platform.

Endpoints:
  POST /research          — Start a research+analysis crew run
  GET  /research/{id}     — Get crew run status and result
  WS   /ws/research/{id}  — Stream crew progress in real time
  GET  /health            — Service health check
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from crew_app import build_crew

logger = logging.getLogger(__name__)

# ── Config ───────────────────────────────────────────────────
RESULTS_DIR = os.getenv("RESULTS_DIR", "./results")
Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)

# ── App ──────────────────────────────────────────────────────
app = FastAPI(
    title="AI Workbench",
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

# In-memory store for running/completed research runs
_research_runs: dict[str, dict[str, Any]] = {}

# ── Endpoints ────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict:
    """Health check — verifies CrewAI and LangFuse config."""
    status = {
        "status": "ok",
        "service": "AI Workbench v2.0.0",
        "crewai": "available",
        "langfuse": "configured" if os.getenv("LANGFUSE_PUBLIC_KEY") else "disabled",
    }
    return status


@app.post("/research")
async def start_research(body: dict[str, Any]):
    """Start a new research run.

    Request body::

        {"topic": "Current state of quantum computing in 2026"}
    """
    topic = body.get("topic", "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    run_id = uuid.uuid4().hex[:12]
    _research_runs[run_id] = {
        "id": run_id,
        "topic": topic,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "result": None,
        "logs": [],
    }

    # Run crew in background
    asyncio.create_task(_run_crew(run_id, topic))

    return {"id": run_id, "status": "pending", "topic": topic}


@app.get("/research/{run_id}")
async def get_research(run_id: str):
    """Get the status and result of a research run."""
    run = _research_runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    return run


@app.get("/research")
async def list_research():
    """List all research runs (newest first)."""
    runs = sorted(
        _research_runs.values(),
        key=lambda r: r["created_at"],
        reverse=True,
    )
    return {"runs": runs[:50]}


@app.websocket("/ws/research/{run_id}")
async def stream_research(ws: WebSocket, run_id: str):
    """Stream crew progress in real time."""
    await ws.accept()

    run = _research_runs.get(run_id)
    if not run:
        await ws.send_json({"type": "error", "message": "Run not found"})
        await ws.close()
        return

    last_log_count = 0
    try:
        while run["status"] not in ("completed", "failed"):
            # Stream new logs
            logs = run.get("logs", [])
            for log in logs[last_log_count:]:
                await ws.send_json(log)
            last_log_count = len(logs)

            await asyncio.sleep(0.5)

        # Send final logs + result
        for log in run.get("logs", [])[last_log_count:]:
            await ws.send_json(log)

        await ws.send_json({
            "type": "complete",
            "status": run["status"],
            "result": run.get("result", ""),
        })
    except WebSocketDisconnect:
        pass


# ── Internal ─────────────────────────────────────────────────

async def _run_crew(run_id: str, topic: str):
    """Execute a CrewAI research run in the background."""
    run = _research_runs.get(run_id)
    if not run:
        return

    run["status"] = "running"
    run["logs"].append({
        "type": "log",
        "level": "info",
        "message": f"Starting research on: {topic}",
    })

    try:
        crew = build_crew(topic)
        result = crew.kickoff()

        run["status"] = "completed"
        run["result"] = str(result)
        run["finished_at"] = datetime.now(timezone.utc).isoformat()
        run["logs"].append({
            "type": "log",
            "level": "info",
            "message": "Research completed successfully",
        })

        # Save to disk
        output_path = Path(RESULTS_DIR) / f"{run_id}.json"
        output_path.write_text(json.dumps(run, indent=2, default=str), encoding="utf-8")

    except Exception as exc:
        logger.exception("Crew run %s failed", run_id)
        run["status"] = "failed"
        run["error"] = str(exc)
        run["finished_at"] = datetime.now(timezone.utc).isoformat()
        run["logs"].append({
            "type": "log",
            "level": "error",
            "message": f"Research failed: {exc}",
        })


@app.get("/")
async def root():
    return {
        "service": "AI Workbench",
        "version": "2.0.0",
        "docs": "/docs",
    }
