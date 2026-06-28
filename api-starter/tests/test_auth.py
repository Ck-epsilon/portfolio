# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Tests for authentication endpoints."""

import asyncio
from httpx import ASGITransport, AsyncClient

# Allow running tests from project root
import sys
sys.path.insert(0, ".")

from app.main import app


def _run(async_fn):
    """Helper: run an async test function in a fresh event loop."""
    return asyncio.run(async_fn)


async def _health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
    return True


def test_health_check():
    assert _run(_health_check())


async def _register_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data
    return True


def test_register_user():
    assert _run(_register_user())


async def _register_duplicate_fails():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        p = {"email": "dup@example.com", "username": "dupuser", "password": "test123456"}
        r1 = await c.post("/auth/register", json=p)
        assert r1.status_code == 201
        r2 = await c.post("/auth/register", json=p)
        assert r2.status_code == 409
    return True


def test_register_duplicate_fails():
    assert _run(_register_duplicate_fails())


async def _login_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        await c.post("/auth/register", json={
            "email": "login@example.com", "username": "loginuser", "password": "secret123",
        })
        r = await c.post("/auth/login", json={"email": "login@example.com", "password": "secret123"})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
    return True


def test_login_success():
    assert _run(_login_success())


async def _login_wrong_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        await c.post("/auth/register", json={
            "email": "wrong@example.com", "username": "wronguser", "password": "correct123",
        })
        r = await c.post("/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
        assert r.status_code == 401
    return True


def test_login_wrong_password():
    assert _run(_login_wrong_password())


async def _auth_required():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.get("/users/")
        # HTTPBearer returns 401 for missing credentials (HTTP standard)
        assert r.status_code == 401
    return True


def test_auth_required_endpoint():
    assert _run(_auth_required())


async def _get_me():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        await c.post("/auth/register", json={
            "email": "mee@example.com", "username": "meuser", "password": "secret123",
        })
        login_r = await c.post("/auth/login", json={
            "email": "mee@example.com", "password": "secret123",
        })
        token = login_r.json()["access_token"]
        r = await c.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "mee@example.com"
        assert data["username"] == "meuser"
    return True


def test_get_me_with_token():
    assert _run(_get_me())


async def _username_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/auth/register", json={
            "email": "short@example.com",
            "username": "ab",  # too short (<3)
            "password": "test123456",
        })
        assert r.status_code == 422
    return True


def test_username_validation():
    assert _run(_username_validation())
