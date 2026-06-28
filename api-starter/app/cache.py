# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Simple cache abstraction — Redis when available, in-memory fallback.

Premium tier: set REDIS_URL in .env to enable Redis caching.
Basic/Standard tier: in-memory dict fallback (not shared across workers).
"""

import json
import time
from typing import Any

from app.config import settings

try:
    import redis.asyncio as aioredis

    _redis_client = aioredis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
except Exception:
    _redis_client = None

# In-memory fallback (not suitable for multi-worker deployments)
_memory_cache: dict[str, tuple[float, Any]] = {}


async def get(key: str) -> Any | None:
    """Get a cached value. Returns None on miss or expiry."""
    if _redis_client:
        raw = await _redis_client.get(key)
        return json.loads(raw) if raw else None

    entry = _memory_cache.get(key)
    if entry is None:
        return None
    expires, value = entry
    if expires and time.time() > expires:
        del _memory_cache[key]
        return None
    return value


async def set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """Set a cached value with optional TTL (default 5 minutes)."""
    if _redis_client:
        await _redis_client.set(key, json.dumps(value), ex=ttl_seconds)
        return

    expires = time.time() + ttl_seconds if ttl_seconds else 0
    _memory_cache[key] = (expires, value)


async def delete(key: str) -> None:
    """Remove a key from cache."""
    if _redis_client:
        await _redis_client.delete(key)
        return

    _memory_cache.pop(key, None)


async def flush() -> None:
    """Clear all cached entries."""
    if _redis_client:
        await _redis_client.flushdb()
        return

    _memory_cache.clear()
