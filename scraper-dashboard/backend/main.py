# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Scraper Pro — Real-time web scraping dashboard backend.

FastAPI application providing REST endpoints for task management,
WebSocket for live log streaming, and CSV export of scrape results.
Premium tier adds: rate limiting, proxy rotation, stealth, DB, alerts, K8s.
"""

import asyncio
import csv
import io
from typing import Any

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from task_queue import TaskManager, TaskStatus
from scraper import scrape_task


# ---------------------------------------------------------------------------
# CSV injection guard
# ---------------------------------------------------------------------------
def _sanitize_csv_cell(value: str) -> str:
    """Prefix cells starting with =, +, -, @ to prevent CSV injection."""
    if not value:
        return value
    if value[0] in "=+-@":
        return "'" + value
    return value


# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------
app = FastAPI(title="Scraper Pro", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

task_manager = TaskManager(max_concurrency=2)


@app.on_event("startup")
async def startup():
    await task_manager.start(scrape_task)


@app.on_event("shutdown")
async def shutdown():
    await task_manager.stop()


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------
@app.post("/tasks")
async def create_task(body: dict[str, Any]):
    """Create a new scrape task.

    Request body::

        {"url": "https://example.com", "config": {"selector": "..."}}
    """
    url = body.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="url is required")
    config = body.get("config", {})
    task = task_manager.create_task(url, config)
    return task.to_dict()


@app.get("/tasks")
async def list_tasks():
    """List all tasks with their current status."""
    return task_manager.list_tasks()


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a single task by ID."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@app.get("/tasks/{task_id}/export")
async def export_task(task_id: str, export_format: str = "csv"):
    """Export task results as CSV (default) or JSON."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.results:
        raise HTTPException(status_code=404, detail="No results to export")

    if export_format == "json":
        return task.results

    # CSV export with injection guard
    output = io.StringIO()
    if task.results:
        fieldnames = list(task.results[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in task.results:
            sanitized = {k: _sanitize_csv_cell(str(v)) for k, v in row.items()}
            writer.writerow(sanitized)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=scrape_{task_id}.csv"
        },
    )


# ---------------------------------------------------------------------------
# WebSocket — real-time log streaming
# ---------------------------------------------------------------------------
@app.websocket("/ws/{task_id}")
async def websocket_logs(websocket: WebSocket, task_id: str):
    """Stream real-time log messages for a specific task.

    Clients connect here to receive ``{type, level, message, ...}`` JSON
    objects as the scraper works through pages.
    """
    await websocket.accept()

    task = task_manager.get_task(task_id)
    if not task:
        await websocket.send_json({"type": "error", "message": "Task not found"})
        await websocket.close()
        return

    # Send historical messages then stream new ones
    try:
        while True:
            try:
                msg = await asyncio.wait_for(task.log_queue.get(), timeout=30.0)
                await websocket.send_json(msg)
            except asyncio.TimeoutError:
                # Send heartbeat to detect disconnected clients
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": f"WebSocket error: {exc}"})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "pending_tasks": task_manager.pending_count,
    }
