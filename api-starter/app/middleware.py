# Author: Ck.epsilon
"""FastAPI middleware: Request ID generation and slow-request detection."""

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging import logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject X-Request-ID header into every response and log request lifecycle.

    Uses existing X-Request-ID header if present in the request (for
    distributed tracing), otherwise generates a new UUID.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:12])
        request.state.request_id = request_id
        logger.configure(extra={"request_id": request_id})  # type: ignore[attr-defined]

        logger.info("→ {} {}", request.method, request.url.path)

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class SlowRequestMiddleware(BaseHTTPMiddleware):
    """Log a warning for requests that take longer than threshold_ms (default 500ms)."""
    def __init__(self, app, threshold_ms: int = 500):
        super().__init__(app)
        self.threshold_ms = threshold_ms

    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        elapsed_ms = (time.monotonic() - start) * 1000
        if elapsed_ms > self.threshold_ms:
            logger.warning(
                "Slow request: {} {} took {:.0f}ms (threshold={}ms)",
                request.method, request.url.path, elapsed_ms, self.threshold_ms,
            )
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.0f}"
        return response
