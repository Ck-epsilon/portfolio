# Author: Ck.epsilon
"""Test fixtures: clean database state per module."""

import asyncio

import pytest

from app import database


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
