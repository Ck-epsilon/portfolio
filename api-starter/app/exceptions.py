# Author: Ck.epsilon
"""Global exception handlers — production-safe error responses.

Every error response includes:
- request_id: for log correlation
- detail: human-readable message (no stack traces, no internal paths)
- type: error classification for client-side handling

Uses middleware for unhandled exceptions (most reliable in Starlette stack)
and FastAPI's standard exception_handler for HTTP/validation errors.
"""

import traceback

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging import logger


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTPException: return standard error with request_id."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        "HTTP {} at {} {}: {}",
        exc.status_code, request.method, request.url.path, exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_error",
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors: 422 with field-level details."""
    request_id = getattr(request.state, "request_id", "unknown")
    errors = exc.errors()
    logger.info("Validation error at {} {}: {} errors", request.method, request.url.path, len(errors))
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed",
            "type": "validation_error",
            "request_id": request_id,
            "errors": [
                {
                    "field": " -> ".join(str(loc) for loc in e["loc"]),
                    "message": e["msg"],
                    "type": e["type"],
                }
                for e in errors
            ],
        },
        headers={"X-Request-ID": request_id},
    )


class CatchAllExceptionMiddleware(BaseHTTPMiddleware):
    """Catch-all: traps any unhandled exception, logs it, returns safe 500.

    Must be the OUTERMOST middleware so it wraps the entire app.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.exception(
                "Unhandled exception at {} {}: {}",
                request.method, request.url.path, type(exc).__name__,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal error occurred. Please include this request ID when contacting support.",
                    "type": "internal_error",
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )
