# Author: Ck.epsilon
"""Integration tests for user CRUD and file upload endpoints."""

import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import app


def _run(async_fn):
    return asyncio.run(async_fn)


# ---- Helpers ----

async def _register_and_login(client, email, username, password):
    """Register a new user and return auth token."""
    r = await client.post("/auth/register", json={
        "email": email, "username": username, "password": password,
    })
    assert r.status_code == 201
    r = await client.post("/auth/login", json={
        "email": email, "password": password,
    })
    assert r.status_code == 200
    return r.json()["access_token"]


# ---- User CRUD ----

async def _get_me_returns_profile():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        token = await _register_and_login(c, "me@test.com", "me_user", "testpass123")
        r = await c.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "me@test.com"
        assert data["username"] == "me_user"
        assert "hashed_password" not in data
    return True


def test_get_me_returns_profile():
    assert _run(_get_me_returns_profile())


async def _update_me_username():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        token = await _register_and_login(c, "update@test.com", "oldname", "testpass123")
        r = await c.patch("/users/me", json={"username": "newname"}, headers={
            "Authorization": f"Bearer {token}",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "newname"
    return True


def test_update_me_username():
    assert _run(_update_me_username())


async def _update_me_duplicate_username():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        await _register_and_login(c, "dup1@test.com", "dup1", "testpass123")
        token = await _register_and_login(c, "dup2@test.com", "dup2", "testpass123")
        # Try to change dup2's username to dup1 (already taken)
        r = await c.patch("/users/me", json={"username": "dup1"}, headers={
            "Authorization": f"Bearer {token}",
        })
        assert r.status_code == 409
        assert "already taken" in r.json()["detail"]
    return True


def test_update_me_duplicate_username():
    assert _run(_update_me_duplicate_username())


async def _list_users():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        token = await _register_and_login(c, "lister@test.com", "lister", "testpass123")
        # Register a second user too
        await c.post("/auth/register", json={
            "email": "other@test.com", "username": "otheruser", "password": "testpass123",
        })
        r = await c.get("/users/", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # at least lister + otheruser
    return True


def test_list_users():
    assert _run(_list_users())


async def _list_users_with_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        token = await _register_and_login(c, "search_test@test.com", "searcher", "testpass123")
        # Register unique user to search for
        await c.post("/auth/register", json={
            "email": "unique@test.com", "username": "unique_user_42", "password": "testpass123",
        })
        r = await c.get("/users/?search=unique_user", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert data[0]["username"] == "unique_user_42"
    return True


def test_list_users_with_search():
    assert _run(_list_users_with_search())


async def _get_user_by_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        token = await _register_and_login(c, "viewer@test.com", "viewer", "testpass123")
        # Register target user
        r = await c.post("/auth/register", json={
            "email": "target@test.com", "username": "target_user", "password": "testpass123",
        })
        target_id = r.json()["id"]
        r = await c.get(f"/users/{target_id}", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["username"] == "target_user"
    return True


def test_get_user_by_id():
    assert _run(_get_user_by_id())


async def _get_user_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        token = await _register_and_login(c, "finder@test.com", "finder", "testpass123")
        r = await c.get("/users/nonexistent-id", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 404
    return True


def test_get_user_not_found():
    assert _run(_get_user_not_found())


async def _list_my_items():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        token = await _register_and_login(c, "items@test.com", "itemsuser", "testpass123")
        r = await c.get("/users/me/items", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 2
    return True


def test_list_my_items():
    assert _run(_list_my_items())


# ---- File Upload ----

async def _upload_file():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        token = await _register_and_login(c, "uploader@test.com", "uploader", "testpass123")
        r = await c.post("/upload/", files={"file": ("test.txt", b"Hello, File Upload!")}, headers={
            "Authorization": f"Bearer {token}",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["filename"] == "test.txt"
        assert data["size_bytes"] == len(b"Hello, File Upload!")
        assert data["uploaded_by"] == "uploader"
    return True


def test_upload_file():
    assert _run(_upload_file())


async def _upload_without_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        r = await c.post("/upload/", files={"file": ("test.txt", b"data")})
        assert r.status_code == 401
    return True


def test_upload_without_auth():
    assert _run(_upload_without_auth())
