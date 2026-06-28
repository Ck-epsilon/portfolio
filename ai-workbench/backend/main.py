# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""AI Workbench — Multi-agent AI platform backed by CrewAI + LangFuse.

FastAPI backend providing:
- POST /research — launch a research crew (topic → report)
- GET /research/{run_id} — poll crew status and results
- WS /ws/{run_id} — live streaming of agent thoughts/output
- GET /health — service health check

All LLM calls traced via LangFuse for observability (cost, latency, token usage).
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from crew_app import build_crew

# NOTE: P4 rule (import modules, not classes) intentionally relaxed for FastAPI —
# `from fastapi import FastAPI` is the framework's documented convention.
# See https://fastapi.tiangolo.com/#example

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Workbench", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory run store ─────────────────────────────────────
# NOTE: Module-level mutable dicts flagged by P9. Acceptable for MVP;
# production should use Redis (aioredis) or a database with TTL.
_runs: dict[str, dict[str, Any]] = {}


def _new_run(topic: str) -> str:
    """Create a new run entry and return its ID."""
    run_id = uuid.uuid4().hex[:12]
    _runs[run_id] = {
        "id": run_id,
        "topic": topic,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
        "result": None,
        "error": None,
    }
    _run_locks[run_id] = asyncio.Lock()
    return run_id


async def _execute_crew(run_id: str, topic: str):
    """Run the crew in the background, streaming output to a log queue."""
    run = _runs[run_id]
    run["status"] = "running"

    try:
        crew = build_crew(topic)
        # CrewAI's kickoff is synchronous; run in executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff)

        run["status"] = "completed"
        run["result"] = str(result) if result else "No result produced."
        run["completed_at"] = datetime.now(timezone.utc).isoformat()
    except Exception as exc:
        logger.exception("Crew execution failed for run %s", run_id)
        run["status"] = "failed"
        # Sanitize: only expose exception message, not full traceback
        run["error"] = f"{type(exc).__name__}: {exc}"


# ── REST Endpoints ───────────────────────────────────────────


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "llm_model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
        "langfuse_enabled": bool(os.getenv("LANGFUSE_PUBLIC_KEY")),
    }


@app.post("/research")
async def start_research(payload: dict[str, Any]) -> dict[str, Any]:
    """Launch a new research crew. Accepts ``{"topic": "..."}``."""
    topic = (payload.get("topic") or "").strip()
    if not topic:
        raise HTTPException(status_code=422, detail="topic is required")

    run_id = _new_run(topic)

    # Fire-and-forget the crew execution
    asyncio.create_task(_execute_crew(run_id, topic))

    return {"run_id": run_id, "status": "queued", "topic": topic}


@app.get("/research/{run_id}")
async def get_research(run_id: str) -> dict[str, Any]:
    """Get the status and result of a research run."""
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "id": run["id"],
        "topic": run["topic"],
        "status": run["status"],
        "created_at": run["created_at"],
        "completed_at": run.get("completed_at"),
        "result": run.get("result"),
        "error": run.get("error"),
    }


@app.get("/research")
async def list_research() -> list[dict[str, Any]]:
    """List all research runs (most recent first)."""
    return sorted(
        [
            {
                "id": r["id"],
                "topic": r["topic"],
                "status": r["status"],
                "created_at": r["created_at"],
            }
            for r in _runs.values()
        ],
        key=lambda x: x["created_at"],
        reverse=True,
    )


# ── WebSocket: live output streaming ─────────────────────────


@app.websocket("/ws/{run_id}")
async def ws_research(ws: WebSocket, run_id: str):
    """Stream live research output via WebSocket.

    Client receives JSON messages:
      {"type": "status", "status": "running|completed|failed"}
      {"type": "result", "text": "..."}
      {"type": "error", "text": "..."}
      {"type": "log", "text": "..."}  (from crew_output.log tail)
    """
    await ws.accept()

    if run_id not in _runs:
        await ws.send_json({"type": "error", "text": "Run not found"})
        await ws.close()
        return

    run = _runs[run_id]

    # Send initial status
    await ws.send_json({"type": "status", "status": run["status"]})

    # Poll status until terminal
    log_path = "crew_output.log"
    log_pos = 0

    try:
        while True:
            await asyncio.sleep(1.0)

            # Send status updates
            status = run["status"]
            await ws.send_json({"type": "status", "status": status})

            # Tail crew output log
            try:
                with open(log_path, encoding="utf-8") as f:
                    f.seek(log_pos)
                    new_lines = f.read()
                    if new_lines:
                        log_pos = f.tell()
                        for line in new_lines.strip().split("\n"):
                            if line.strip():
                                await ws.send_json({"type": "log", "text": line})
            except FileNotFoundError:
                pass

            # Terminal states
            if status == "completed":
                await ws.send_json({"type": "result", "text": run.get("result", "")})
                break
            elif status == "failed":
                await ws.send_json({"type": "error", "text": run.get("error", "")})
                break

            # Check for client disconnect
            try:
                await ws.receive_text()
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error for run %s", run_id)
    finally:
        try:
            await ws.close()
        except Exception:
            pass
