# Author: Ck.epsilon
"""Integration tests for auth, health, root, and token endpoints — 12 tests with DB isolation."""

import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import app


def _run(async_fn):
    """Helper: run an async test function. Each test gets a fresh event loop
    and DB isolation is guaranteed by conftest.py `clean_db`."""
    return asyncio.run(async_fn)


# ---- Infrastructure ----

async def _health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("ok", "degraded")
        assert "version" in data
        assert "database" in data
    return True


def test_health_check():
    assert _run(_health_check())


async def _root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["app"] == "API Starter"
    return True


def test_root():
    assert _run(_root())


# ---- Authentication ----

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
        assert "already exists" in r2.json()["detail"]
    return True


def test_register_duplicate_fails():
    assert _run(_register_duplicate_fails())


async def _login_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        await c.post("/auth/register", json={
            "email": "login@example.com", "username": "loginuser", "password": "secret123",
        })
        r = await c.post("/auth/login", json={
            "email": "login@example.com", "password": "secret123",
        })
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
        r = await c.post("/auth/login", json={
            "email": "wrong@example.com", "password": "wrong",
        })
        assert r.status_code == 401
        assert "Invalid email or password" in r.json()["detail"]
    return True


def test_login_wrong_password():
    assert _run(_login_wrong_password())


async def _auth_required_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.get("/users/me")
        assert r.status_code == 401
    return True


def test_auth_required_endpoint():
    assert _run(_auth_required_endpoint())


async def _get_me_with_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        await c.post("/auth/register", json={
            "email": "me@example.com", "username": "meuser", "password": "mypassword",
        })
        login_r = await c.post("/auth/login", json={
            "email": "me@example.com", "password": "mypassword",
        })
        token = login_r.json()["access_token"]
        r = await c.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "me@example.com"
        assert "hashed_password" not in data
    return True


def test_get_me_with_token():
    assert _run(_get_me_with_token())


async def _username_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/auth/register", json={
            "email": "short@example.com",
            "username": "ab",
            "password": "testpass123",
        })
        assert r.status_code == 422
    return True


def test_username_validation():
    assert _run(_username_validation())


async def _missing_field_returns_422():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/auth/register", json={
            "email": "missing@example.com",
        })
        assert r.status_code == 422
    return True


def test_missing_field_returns_422():
    assert _run(_missing_field_returns_422())


async def _token_refresh():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        await c.post("/auth/register", json={
            "email": "refresh@example.com", "username": "refreshuser", "password": "refresh123",
        })
        login_r = await c.post("/auth/login", json={
            "email": "refresh@example.com", "password": "refresh123",
        })
        refresh_token = login_r.json()["refresh_token"]
        r = await c.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
    return True


def test_token_refresh():
    assert _run(_token_refresh())


async def _token_refresh_invalid():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/auth/refresh", json={"refresh_token": "invalid.token.here"})
        assert r.status_code == 401
    return True


def test_token_refresh_invalid():
    assert _run(_token_refresh_invalid())
