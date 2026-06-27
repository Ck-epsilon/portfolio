# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Async task queue manager for Scraper Pro.

Manages scrape task lifecycle: creation, queuing, execution, and result storage.
Uses asyncio.Queue for FIFO task processing with configurable concurrency.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a single scrape task and its lifecycle state."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    url: str = ""
    config: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    log_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    results: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str = ""
    rows_scraped: int = 0
    pages_scraped: int = 0
    current_page: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize task metadata (excludes log_queue for JSON)."""
        return {
            "id": self.id,
            "url": self.url,
            "config": self.config,
            "status": self.status.value,
            "results": self.results,
            "error": self.error,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "rows_scraped": self.rows_scraped,
            "pages_scraped": self.pages_scraped,
            "current_page": self.current_page,
        }


class TaskManager:
    """Manages the lifecycle of scrape tasks with an async worker pool."""

    def __init__(self, max_concurrency: int = 2):
        self._tasks: dict[str, Task] = {}
        self._queue: asyncio.Queue[Task] = asyncio.Queue()
        self._max_concurrency = max_concurrency
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._running = False
        self._workers: list[asyncio.Task] = []

    async def start(self, process_task):
        """Start worker coroutines. *process_task* is an async callable that
        receives a Task and processes it (must update task.status and push
        log messages to task.log_queue)."""
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(process_task))
            for _ in range(self._max_concurrency)
        ]

    async def stop(self):
        """Cancel all running workers."""
        self._running = False
        for w in self._workers:
            w.cancel()
        self._workers.clear()

    async def _worker(self, process_task):
        """Continuously pull tasks from the queue and execute them."""
        while self._running:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            async with self._semaphore:
                try:
                    task.status = TaskStatus.RUNNING
                    await task.log_queue.put({
                        "type": "status", "status": "running", "message": "Task started"
                    })
                    await process_task(task)
                except asyncio.CancelledError:
                    task.status = TaskStatus.CANCELLED
                    break
                except Exception as exc:
                    task.status = TaskStatus.FAILED
                    task.error = str(exc)
                    await task.log_queue.put({
                        "type": "error", "message": f"Task failed: {exc}"
                    })
                finally:
                    if task.status == TaskStatus.RUNNING:
                        task.status = TaskStatus.COMPLETED
                    task.finished_at = datetime.now(timezone.utc).isoformat()
                    self._queue.task_done()

    def create_task(self, url: str, config: Optional[dict] = None) -> Task:
        """Create a new task, enqueue it, and return it."""
        task = Task(url=url, config=config or {})
        self._tasks[task.id] = task
        self._queue.put_nowait(task)
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[dict[str, Any]]:
        """Return serialized metadata for all known tasks."""
        return [t.to_dict() for t in self._tasks.values()]

    @property
    def pending_count(self) -> int:
        return self._queue.qsize()
