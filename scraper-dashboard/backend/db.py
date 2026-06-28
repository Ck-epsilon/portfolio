# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""
SQLite task history database for the AI Workbench.
Persists agent conversations, tool calls, and task outcomes.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "workbench.db"


def get_db() -> sqlite3.Connection:
    """Get a connection to the workbench database. Creates tables if needed."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL,
            user_message TEXT,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            status TEXT DEFAULT 'running',
            error TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(id),
            role TEXT NOT NULL,
            content TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tool_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL REFERENCES tasks(id),
            tool_name TEXT NOT NULL,
            arguments TEXT,
            result TEXT,
            created_at TEXT NOT NULL
        );
    """)


def create_task(agent_name: str, user_message: str) -> str:
    """Create a new task record and return its ID."""
    task_id = uuid.uuid4().hex[:12]
    now = datetime.utcnow().isoformat()
    conn = get_db()
    conn.execute(
        "INSERT INTO tasks (id, agent_name, user_message, started_at) VALUES (?, ?, ?, ?)",
        (task_id, agent_name, user_message, now),
    )
    conn.commit()
    conn.close()
    logger.info("Task %s created for agent '%s'", task_id, agent_name)
    return task_id


def add_message(task_id: str, role: str, content: str):
    """Record a conversation message."""
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (task_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (task_id, role, content, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def add_tool_call(task_id: str, tool_name: str, arguments: dict, result: Optional[str]):
    """Record a tool call and its result."""
    conn = get_db()
    conn.execute(
        "INSERT INTO tool_calls (task_id, tool_name, arguments, result, created_at) VALUES (?, ?, ?, ?, ?)",
        (task_id, tool_name, json.dumps(arguments), result, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def finish_task(task_id: str, status: str = "completed", error: str | None = None):
    """Mark a task as completed or failed."""
    conn = get_db()
    conn.execute(
        "UPDATE tasks SET finished_at = ?, status = ?, error = ? WHERE id = ?",
        (datetime.utcnow().isoformat(), status, error, task_id),
    )
    conn.commit()
    conn.close()


def get_task_history(agent_name: str | None = None, limit: int = 20) -> list[dict]:
    """Get recent task history, optionally filtered by agent."""
    conn = get_db()
    if agent_name:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE agent_name = ? ORDER BY started_at DESC LIMIT ?",
            (agent_name, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM tasks ORDER BY started_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
