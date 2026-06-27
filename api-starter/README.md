# FastAPI Starter — Production-Ready Scaffold

Clean FastAPI project scaffold with JWT authentication, async SQLAlchemy, and automatic Swagger documentation. Ready to deploy in minutes.

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for interactive API docs.

## Project Structure

```
api-starter/
├── app/
│   ├── main.py          # App entry point, middleware, health check
│   ├── config.py        # Environment-based settings
│   ├── database.py      # Async SQLAlchemy engine + sessions
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   └── routers/         # API route handlers
├── tests/               # pytest test suite
├── requirements.txt
└── README.md
```

## Features

- FastAPI with async support
- Automatic OpenAPI / Swagger UI
- CORS middleware pre-configured
- SQLAlchemy 2.0 async with PostgreSQL/SQLite
- JWT authentication (login, refresh, logout)
- Pydantic v2 request validation
- Health check endpoint
- Docker-ready
