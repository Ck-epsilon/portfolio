# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Redis-backed rate limiting middleware with sliding window algorithm."""

import asyncio
import time
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    import redis.asyncio as aioredis

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging import logger
from app.redis_client import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter backed by Redis.

    Each client is identified by IP + route. In-memory fallback when Redis is
    unavailable (not suitable for multi-process deployments).

    Configurable via app.state or environment:
        RATE_LIMIT_MAX_REQUESTS (default: 100)
        RATE_LIMIT_WINDOW_SECONDS (default: 60)
    """

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
        exempt_paths: tuple[str, ...] = ("/health", "/docs", "/redoc", "/openapi.json"),
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exempt_paths = exempt_paths
        # In-memory fallback (per-worker, not shared)
        self._inmemory: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        client_id = self._get_client_id(request)
        route_key = f"{client_id}:{request.url.path}"

        redis = await get_redis()
        if redis is not None:
            allowed = await self._check_redis(route_key, redis)
        else:
            allowed = await self._check_inmemory(route_key)

        if not allowed:
            logger.warning("Rate limit hit", client=client_id, path=request.url.path)
            return Response(
                content='{"detail":"Too many requests"}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(self.window_seconds)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        return response

    def _get_client_id(self, request: Request) -> str:
        """Identify client by X-Forwarded-For or client IP."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def _check_redis(self, key: str, redis: "aioredis.Redis") -> bool:
        """Sliding window via Redis sorted set."""
        now_ms = int(time.time() * 1000)
        window_start = now_ms - self.window_seconds * 1000

        async with redis.pipeline(transaction=True) as pipe:
            # Remove timestamps outside the window
            pipe.zremrangebyscore(key, 0, window_start)
            # Count current requests in the window
            pipe.zcard(key)
            # Add current request
            pipe.zadd(key, {str(now_ms): now_ms})
            # Set key expiry (slightly longer than window)
            pipe.expire(key, self.window_seconds + 10)
            _, count, _, _ = await pipe.execute()

        return count < self.max_requests

    async def _check_inmemory(self, key: str) -> bool:
        """In-memory sliding window fallback (single-process only). Lock-protected."""
        async with self._lock:
            now = time.time()
            window_start = now - self.window_seconds
            timestamps = self._inmemory.get(key, [])
            # Prune old entries
            timestamps = [t for t in timestamps if t > window_start]
            self._inmemory[key] = timestamps
            if len(timestamps) >= self.max_requests:
                return False
            timestamps.append(now)
            return True
