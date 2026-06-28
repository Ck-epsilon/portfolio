# Author: Ck.epsilon
"""FastAPI Starter — production-ready scaffold with JWT auth and async database."""

from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import create_tables, engine
from app.exceptions import (
    CatchAllExceptionMiddleware,
    http_exception_handler,
    validation_exception_handler,
)
from app.logging import logger
from app.middleware import RequestIDMiddleware, SlowRequestMiddleware
from app.routers import auth, uploads, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables. Shutdown: dispose engine connections."""
    logger.info("Starting {} v{}", settings.APP_NAME, settings.APP_VERSION)
    await create_tables()
    yield
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready FastAPI scaffold with JWT auth, structured logging, and async database.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---- Middleware (order matters: first added = outermost) ----
# CatchAllExceptionMiddleware MUST be outermost to catch all exceptions
app.add_middleware(CatchAllExceptionMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SlowRequestMiddleware, threshold_ms=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Exception handlers ----
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(uploads.router)


@app.get("/")
async def root():
    """API root — redirect to /docs for interactive documentation."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    """Health check — verifies database connectivity, returns version."""
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        logger.warning("Health check: database unreachable")

    return {
        "status": "ok" if db_ok else "degraded",
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "unreachable",
    }


# ---- Background Tasks (Premium tier) ----

def _long_task(message: str):
    """Simulate a background task. In production, replace with real work."""
    import time
    time.sleep(2)
    logger.debug("Background task completed: {}", message)


@app.post("/tasks/demo")
async def demo_background_task(
    request: Request,
    message: str = "Hello from background task!",
    background_tasks: BackgroundTasks = None,
):
    """Demo: enqueue a background task. Returns immediately, task runs async."""
    req_log = logger.bind(request_id=request.state.request_id)
    req_log.info("Background task enqueued: {}", message)
    if background_tasks:
        background_tasks.add_task(_long_task, message)
    return {"status": "accepted", "message": message}


# ---- WebSocket (Premium tier) ----

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Simple echo WebSocket. Accepts connection, echoes messages back."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass


# ---- Internal only: endpoint to verify 500 handling (do not expose in production) ----

@app.get("/trigger-500")
async def trigger_500():
    """Deliberately raises an exception to verify error handling.
    NOT for production use — included as a test hook."""
    raise RuntimeError("Intentional error for testing 500 handler")
