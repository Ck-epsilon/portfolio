# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Pytest fixtures for api-starter tests."""

import asyncio
import pytest

from app.database import create_tables


@pytest.fixture(scope="session", autouse=True)
def _init_db():
    """Create DB tables once before any test. Idempotent (CREATE TABLE IF NOT EXISTS)."""
    asyncio.run(create_tables())
