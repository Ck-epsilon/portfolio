# FastAPI Starter — Ship Your API in 5 Minutes

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-38%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-83%25-yellow)](htmlcov/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED)](https://www.docker.com/)

**You're billing $150–300 on Fiverr to build a backend. You don't want to start from zero.**

This is the scaffold you clone, run `docker compose up`, and have **JWT auth, async database, structured logging, file upload, and full test coverage** in one command. 14 endpoints, production error handling, request tracing, health checks that actually verify the database — not "everything is fine" lies.

---

## What You Get

```bash
$ docker compose up
✔ API running at http://localhost:8000/docs
✔ 14 endpoints with interactive Swagger docs
✔ Structured logging with request IDs
✔ Health check that verifies DB connectivity
✔ JWT auth with refresh tokens & bcrypt
✔ 38 tests, 83% coverage
```

---

## Quick Start

```bash
git clone https://github.com/Ck-epsilon/portfolio.git
cd portfolio/api-starter
cp .env.example .env
docker compose up
```

Open **[http://localhost:8000/docs](http://localhost:8000/docs)** — interactive Swagger UI with every endpoint ready to call.

No `pip install`, no database setup, no manual migrations. Docker handles everything.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      HTTP Requests                       │
└─────────────────────┬───────────────────────────────────┘
                      │
    ┌─────────────────▼──────────────────┐
    │   CatchAllExceptionMiddleware      │  ← 500 → safe JSON, no stack traces
    │   RequestIDMiddleware              │  ← X-Request-ID on every response
    │   SlowRequestMiddleware            │  ← Warnings for >500ms requests
    │   CORSMiddleware                   │
    └─────────────────┬──────────────────┘
                      │
    ┌─────────────────▼──────────────────┐
    │           API Router                │
    │  ┌──────────┬──────────┬────────┐  │
    │  │  /auth   │  /users  │ /upload│  │
    │  │ register │  list    │  POST  │  │
    │  │ login    │  get     │        │  │
    │  │ refresh  │  update  │        │  │
    │  │ forgot   │  delete  │        │  │
    │  │ reset    │  items   │        │  │
    │  └──────────┴──────────┴────────┘  │
    └─────────────────┬──────────────────┘
                      │
    ┌─────────────────▼──────────────────┐
    │  SQLAlchemy 2.0 Async Engine        │
    │  ┌─────────────┬─────────────────┐  │
    │  │ SQLite (dev)│ PostgreSQL (prod)│  │
    │  └─────────────┴─────────────────┘  │
    └─────────────────────────────────────┘
```

**Request lifecycle (authenticated):**

```
Client → RequestID (UUID assigned) → CORS check → Auth dependency (JWT verify)
       → Route handler → DB session → Response + X-Request-ID header
       → SlowRequest check (>500ms?) → Logged with request_id → Client
```

---

## All Endpoints

Every endpoint below has a **copy-paste curl command**. Register once, grab a token, and test everything in under 2 minutes.

### Health

```bash
curl http://localhost:8000/health
# {"status":"ok","version":"1.1.0","database":"connected"}
```

### Register & Login

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","username":"alice","password":"securepass123"}'

# Login (save the access_token)
export TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"securepass123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo $TOKEN
```

### Get Current User

```bash
curl http://localhost:8000/users/me -H "Authorization: Bearer $TOKEN"
# {"id":"...","email":"alice@example.com","username":"alice","is_active":true,...}
```

Also available at `/auth/me` (same result, different router path).

### List Users (with search & sort)

```bash
# All users
curl "http://localhost:8000/users/" -H "Authorization: Bearer $TOKEN"

# Search
curl "http://localhost:8000/users/?search=bob" -H "Authorization: Bearer $TOKEN"

# Sorted
curl "http://localhost:8000/users/?sort_by=username&order=desc" -H "Authorization: Bearer $TOKEN"

# Paginated
curl "http://localhost:8000/users/?skip=0&limit=5" -H "Authorization: Bearer $TOKEN"
```

### Get User by ID

```bash
curl http://localhost:8000/users/{user_id} -H "Authorization: Bearer $TOKEN"
```

### Update Profile

```bash
curl -X PATCH http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_new"}'
```

### Token Refresh

```bash
REFRESH=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"securepass123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['refresh_token'])")

curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH\"}"
# Returns new access_token + refresh_token pair
```

### Password Reset Flow

```bash
# Step 1: Request reset token
curl -X POST http://localhost:8000/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com"}'
# Returns reset token (emailed in production)

# Step 2: Reset password
curl -X POST http://localhost:8000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token":"<reset_token>","new_password":"newsecure456"}'
```

### File Upload

```bash
echo "Hello from file upload" > test.txt
curl -X POST http://localhost:8000/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.txt"
# {"filename":"test.txt","saved_as":"<uuid>.txt","size_bytes":23,"uploaded_by":"alice"}
```

### Background Tasks

```bash
curl -X POST "http://localhost:8000/tasks/demo?message=Hello+World"
# {"status":"accepted","message":"Hello World"}
```

### WebSocket

```bash
# Connect via any WebSocket client:
wscat -c ws://localhost:8000/ws
> hello
< Echo: hello
```

---

## Every Error Response Includes `request_id`

```json
{
  "detail": "Invalid email or password",
  "type": "http_error",
  "request_id": "a3f2b1c9d4e5"
}
```

All responses carry `X-Request-ID` and `X-Response-Time-Ms` headers. Find the matching log entry instantly:

```
2026-06-28 10:12:26.488 | INFO     | a3f2b1c9d4e5 | → POST /auth/login
2026-06-28 10:12:26.500 | INFO     | a3f2b1c9d4e5 | User logged in: alice (alice@example.com)
```

---

## Why This Template?

| Feature | This Template | cookiecutter-fastapi | full-stack-fastapi-template |
|---------|:---:|:---:|:---:|
| Docker one-command start | ✅ | ❌ | ❌ |
| Structured logging + request IDs | ✅ | ❌ | ❌ |
| Health check verifies DB | ✅ | ❌ | ❌ |
| Production error handling (no stack leaks) | ✅ | ❌ | Partial |
| 38 integration tests + DB isolation | ✅ | ❌ | Partial |
| JWT auth (bcrypt, refresh, reset) | ✅ | ✅ | ✅ |
| Async SQLAlchemy 2.0 | ✅ | ❌ | ✅ |
| Rate limiting (slowapi) | ✅ | ❌ | ✅ |
| Makefile DX targets | ✅ | ❌ | ❌ |

**This template is for you if:**
- You sell backend development on Fiverr and need a reliable starting point
- You care about observability (structured logs, request IDs, slow request detection)
- You've been burned by "works on my machine" and want Docker from day one
- You need production error handling that doesn't leak stack traces to clients

---

## Production Deployment

### Docker (any VPS)

```bash
# On your server:
git clone https://github.com/Ck-epsilon/portfolio.git
cd portfolio/api-starter
cp .env.example .env
# Generate a real secret key:
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Paste into .env as SECRET_KEY
# Set CORS_ORIGINS to your frontend domain
docker compose up -d
```

### Railway

1. Connect GitHub repo
2. Set root directory to `api-starter`
3. Add environment variables from `.env.example`
4. Deploy — Railway auto-detects Dockerfile

### Render

1. Create new Web Service
2. Connect repo, root: `api-starter`
3. Runtime: Docker
4. Add env vars: `DATABASE_URL` (use Render PostgreSQL), `SECRET_KEY`

---

## FAQ

**Why bcrypt instead of passlib?**
Passlib is unmaintained and has breaking changes between versions. bcrypt 4.x is actively maintained and simpler. We made this switch after a production issue where passlib silently changed its default algorithm — see [discussion](https://github.com/pyca/bcrypt).

**Route ordering: why is `/users/me` before `/{user_id}`?**
FastAPI matches routes in registration order. If `/{user_id}` came first, `me` would be treated as a UUID lookup and return 404. We order specific paths (`/me`, `/me/items`) before parameterized ones.

**Is this safe for concurrent requests?**
Yes. SQLAlchemy async sessions are request-scoped (via `Depends(get_db)`), and SQLite is configured with `check_same_thread=False` for async access. For production, switch to PostgreSQL for row-level locking.

**What about database migrations?**
For zero-config quick start, tables are created via SQLAlchemy `create_all()` in the lifespan. In production, add Alembic — the model structure is ready for migration versioning.

**Security audit?**
- Passwords hashed with bcrypt (not SHA or MD5)
- JWT keys stored in env vars (`.env` in `.gitignore`)
- `SECRET_KEY` defaults to a placeholder — fails loudly if unchanged in production
- No stack traces in 500 responses
- `401` never distinguishes "user not found" from "wrong password" (prevents email enumeration)

---

## Project Structure

```
api-starter/
├── app/
│   ├── main.py              # App entry + middleware + exception handlers
│   ├── config.py            # Environment-based settings (pydantic-settings)
│   ├── database.py          # Async SQLAlchemy engine + session management
│   ├── logging.py           # Structured logging (loguru)
│   ├── middleware.py         # RequestID + SlowRequest middleware
│   ├── exceptions.py        # Global exception handlers + CatchAllMiddleware
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # API route handlers (auth, users, uploads)
│   └── auth/                # JWT utils + auth dependencies
├── tests/
│   ├── conftest.py          # DB isolation fixtures
│   ├── test_auth.py         # 12 auth + health + root tests
│   ├── test_crud.py         # 10 user CRUD + file upload tests
│   ├── test_errors.py       # 4 error handling safety tests
│   └── test_edge.py         # 7 edge case tests (reset flow, admin, bg tasks)
├── .coveragerc              # Coverage configuration
├── .pre-commit-config.yaml  # Ruff + mypy hooks
├── docker-compose.yml       # Dev (hot reload) + production profiles
├── Dockerfile               # python:3.11-slim
├── Makefile                 # setup / dev / test / lint / clean
├── requirements.txt
└── pytest.ini
```

---

## Development

```bash
make setup     # Install deps + pre-commit hooks
make dev       # Start with hot reload
make test      # Run 38 tests with coverage
make lint      # Ruff check + mypy
make format    # Auto-format code
make clean     # Remove cache artifacts
```

Pre-commit hooks (`.pre-commit-config.yaml`) run `ruff` and `mypy` on every commit.

---

*Author: Ck.epsilon*

---

**License:** MIT. Use this for your Fiverr gigs, SaaS backends, or hackathon projects. If this saved you an hour, consider starring the repo.
