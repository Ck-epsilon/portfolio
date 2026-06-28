# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Redis connection manager with lazy initialization and fallback to no-op cache."""

import json
from functools import wraps
from typing import Any, Callable, Optional

from app.config import settings
from app.logging import logger

_redis: Optional["aioredis.Redis"] = None  # type: ignore[name-defined]
_redis_checked: bool = False
REDIS_AVAILABLE: bool = False


async def _connect_redis() -> Optional["aioredis.Redis"]:  # type: ignore[name-defined]
    """Lazily connect to Redis. Returns None if unavailable."""
    global _redis, _redis_checked, REDIS_AVAILABLE
    if _redis_checked:
        return _redis

    _redis_checked = True
    try:
        import asyncio
        import redis.asyncio as aioredis

        _redis = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
            health_check_interval=30,
        )
        await asyncio.wait_for(_redis.ping(), timeout=2.0)
        REDIS_AVAILABLE = True
        logger.info("Redis connected at {}", settings.REDIS_URL)
        return _redis
    except Exception as exc:
        REDIS_AVAILABLE = False
        _redis = None  # Don't leak a dead pool object
        logger.warning("Redis unavailable ({}) — caching and rate limiting disabled", exc)
        return None


async def get_redis() -> Optional["aioredis.Redis"]:  # type: ignore[name-defined]
    """Return the Redis connection or None if unavailable."""
    return await _connect_redis()


# ---- Cache Decorator ----

def cached(ttl: int = 300, key_prefix: str = "cache") -> Callable:
    """Decorator: cache async function results in Redis.

    Args:
        ttl: Time-to-live in seconds (default 5 minutes).
        key_prefix: Prefix for the cache key namespace.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            redis = await _connect_redis()
            if redis is None:
                return await func(*args, **kwargs)

            # Build a deterministic cache key from function name + args
            key_parts = [key_prefix, func.__name__]
            key_parts.append(json.dumps(args, default=str))
            key_parts.append(json.dumps(kwargs, default=str, sort_keys=True))
            cache_key = ":".join(key_parts)

            # Try cache hit
            cached_value = await redis.get(cache_key)
            if cached_value is not None:
                logger.debug("Cache hit: {}", cache_key[:80])
                return json.loads(cached_value)

            # Cache miss: execute and store
            result = await func(*args, **kwargs)
            await redis.setex(cache_key, ttl, json.dumps(result, default=str))
            logger.debug("Cache set: {} (TTL={}s)", cache_key[:80], ttl)
            return result

        return wrapper

    return decorator


async def invalidate_cache(pattern: str = "*") -> int:
    """Delete all cache keys matching the given pattern. Returns count deleted."""
    redis = await _connect_redis()
    if redis is None:
        return 0
    keys = await redis.keys(pattern)
    if keys:
        return await redis.delete(*keys)
    return 0
