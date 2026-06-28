# Author: Ck.epsilon
"""Tests for production error handling — no stack traces, request_id everywhere."""

import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import app


def _run(async_fn):
    return asyncio.run(async_fn)


# ---- Request ID on errors ----

async def _all_errors_have_request_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # 404
        r = await c.get("/nonexistent")
        assert "X-Request-ID" in r.headers
        data = r.json()
        assert "request_id" in data
        assert r.status_code == 404

        # 422 (validation)
        r = await c.post("/auth/register", json={"email": "bad"})
        assert "X-Request-ID" in r.headers
        data = r.json()
        assert "request_id" in data
        assert data["type"] == "validation_error"
        assert "errors" in data  # field-level details
        assert r.status_code == 422

        # 401 (unauthorized)
        r = await c.get("/users/me")
        assert "X-Request-ID" in r.headers
        data = r.json()
        assert "request_id" in data
        assert r.status_code == 401
    return True


def test_all_errors_have_request_id():
    assert _run(_all_errors_have_request_id())


# ---- 500 does not leak stack traces ----

async def _internal_error_no_stack_trace():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # This endpoint deliberately raises an exception
        r = await c.get("/trigger-500")
        assert r.status_code == 500
        data = r.json()
        assert "request_id" in data
        assert "type" in data
        assert "traceback" not in str(data).lower()
        assert "File " not in str(data)  # No Python file paths
        assert "line " not in str(data)  # No line numbers
        # Detail should be user-friendly
        assert "internal error" in data["detail"].lower()
    return True


def test_internal_error_no_stack_trace():
    assert _run(_internal_error_no_stack_trace())


# ---- Auth errors never reveal user existence ----

async def _login_never_reveals_user_existence():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # Login with non-existent email
        r = await c.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "anypassword",
        })
        assert r.status_code == 401
        detail = r.json()["detail"].lower()
        # Must NOT reveal whether user doesn't exist or password is wrong
        assert "not found" not in detail
        assert "does not exist" not in detail
        assert "invalid" in detail  # Generic message is fine
    return True


def test_login_never_reveals_user_existence():
    assert _run(_login_never_reveals_user_existence())


# ---- 422 returns field-level error details ----

async def _validation_422_has_field_details():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/auth/register", json={
            "email": "test@example.com",
            "username": "ab",  # too short
            "password": "12",  # too short
        })
        assert r.status_code == 422
        data = r.json()
        assert len(data["errors"]) >= 2  # At least username + password
        fields = [e["field"] for e in data["errors"]]
        assert any("username" in f.lower() for f in fields)
        assert any("password" in f.lower() for f in fields)
    return True


def test_validation_422_has_field_details():
    assert _run(_validation_422_has_field_details())
