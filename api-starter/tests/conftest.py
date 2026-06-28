# Author: Ck.epsilon
"""Test fixtures: clean database state per module, Redis disabled."""

import asyncio
import os

# Disable Redis + Celery before any app modules are imported.
# Rate limiting falls back to in-memory; caching becomes no-op.
os.environ["REDIS_URL"] = ""
os.environ["CELERY_BROKER_URL"] = ""
os.environ["CELERY_RESULT_BACKEND"] = ""

import pytest

from app import database
from app import redis_client


@pytest.fixture(scope="session", autouse=True)
def _disable_redis():
    """Force Redis to unavailable for all tests."""
    redis_client._redis_checked = True
    redis_client._redis = None
    redis_client.REDIS_AVAILABLE = False


@pytest.fixture(scope="session")
def _db_engine():
    """Session-scoped: ensure tables exist, clean up after all tests."""
    async def _create():
        async with database.engine.begin() as conn:
            await conn.run_sync(database.Base.metadata.create_all)
    asyncio.run(_create())
    yield
    async def _drop():
        async with database.engine.begin() as conn:
            await conn.run_sync(database.Base.metadata.drop_all)
    asyncio.run(_drop())


@pytest.fixture(autouse=True)
def clean_db(_db_engine):
    """Before each test: delete all rows to ensure isolation."""
    async def _clean():
        async with database.engine.begin() as conn:
            for table in reversed(database.Base.metadata.sorted_tables):
                await conn.execute(table.delete())
    asyncio.run(_clean())
