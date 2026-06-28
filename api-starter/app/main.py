# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""FastAPI Starter — production-ready scaffold with JWT auth and async database."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create database tables. Shutdown: clean up connections."""
    await create_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready FastAPI scaffold with JWT auth and async database.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — configure origins in .env for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(users.router)


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
    """Health check endpoint."""
    return {"status": "ok", "version": settings.APP_VERSION}
