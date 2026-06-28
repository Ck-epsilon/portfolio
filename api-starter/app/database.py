# Author: Ck.epsilon
"""Async SQLAlchemy engine and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Support both PostgreSQL and SQLite via DATABASE_URL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    # SQLite needs check_same_thread=False for async
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency: yield an async database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables (for SQLite quick start)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
