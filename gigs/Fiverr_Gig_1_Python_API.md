# Fiverr Gig #1: Python REST API Backend

> **Author:** Ck.epsilon
> **Stack:** Python 3.11+ · FastAPI · SQLAlchemy (async) · PostgreSQL · JWT · Docker
> **Portfolio:** [github.com/ck-epsilon](https://github.com/ck-epsilon) *(live previews available on request — portfolio growing weekly)*

## Gig 基本信息

| 字段 | 内容 |
|------|------|
| **Title** | Build a production-ready Python REST API backend — FastAPI or Flask |
| **Category** | Programming & Tech → Software Development → Web Programming |
| **Service Type** | Backend API Development |
| **Price Tiers** | Basic $80 / Standard $150 / Premium $300 |
| **Delivery Time** | 3 / 5 / 7 days |

## Gig Description

**I'll build your Python REST API backend from scratch — clean, documented, and production-ready.**

Need an API for your app, dashboard, or microservice? I deliver FastAPI (or Flask) backends with full CRUD, authentication, database integration, and auto-generated Swagger docs. Every line of code is typed, tested, and ready to deploy.

**What you get:**
- RESTful API endpoints with FastAPI (async, auto-docs) or Flask
- Database integration: SQLite (quick start), PostgreSQL or MySQL (production)
- Authentication: JWT, OAuth2, API keys
- Request validation, error handling, pagination
- OpenAPI/Swagger documentation auto-generated
- Clean, typed Python code (PEP 8, type hints)
- Dockerfile if needed

**Why a custom backend instead of Firebase / Supabase?**
- **Zero vendor lock-in** — your code, your database, your server. Migrate anywhere.
- **Full control** — custom business logic, no API rate limits, no surprise bills.
- **Cheaper at scale** — a $5 VPS runs circles around a $25/month BaaS once you grow.

**What you need to provide:**
- API requirements (endpoints, data models) — I can help scope if you're unsure
- Database preference or I'll default to SQLite (easy to upgrade later)
- Any existing codebase if this is an integration

**Not sure what you need?** Message me first. I'll help you scope it in 1-2 questions.

---

## Price Tiers

### Basic ($80) — 3 Days · ⭐ Most Popular Starter
- 2-4 REST endpoints
- SQLite database (ready to swap to PostgreSQL)
- Basic CRUD operations
- Input validation
- Swagger docs
- README with setup + run instructions

### Standard ($150) — 5 Days · 🔥 Best Value
- 5-10 REST endpoints
- PostgreSQL or MySQL
- JWT authentication (login/register/refresh)
- Role-based access control
- Pagination + filtering + sorting
- File upload endpoint
- Docker + docker-compose

### Premium ($300) — 7 Days · 🚀 Production-Ready
- 10+ REST endpoints
- Full auth system (JWT + refresh + password reset)
- Async background tasks (Celery or FastAPI BackgroundTasks)
- Redis caching layer
- WebSocket support
- Automated tests (pytest, 80%+ coverage)
- CI/CD config (GitHub Actions)
- Deployment guide (to Railway, Render, or your VPS)

---

## FAQ

**Q: What if I need a custom stack (Django, a specific ORM, etc.)?**
A: Message me first with requirements. FastAPI is my default, but I can work with Django, Flask, or raw ASGI.

**Q: Can you integrate with an existing codebase?**
A: Yes. Just share access and describe the integration point.

**Q: Do you provide the source code?**
A: Yes — full source, git history, and setup instructions. No black boxes.

**Q: What if I need revisions?**
A: Each tier includes 2 rounds of revisions. Additional revisions at $25/round.

**Q: What happens after delivery?**
A: You own the code. Deploy it anywhere. I include a deployment guide in the Premium tier. If you need ongoing maintenance, message me for a custom retainer.

**Q: Is my data / business logic safe?**
A: Your code never touches a third-party server during development. I work locally with your repo. No backdoors, no telemetry, no data exfiltration.

---

## Code Template (Deliverable Preview)

When a client orders, this is the scaffold I ship:

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry (lifespan, CORS, routers)
│   ├── config.py         # pydantic-settings, .env support
│   ├── database.py       # Async SQLAlchemy engine + session
│   ├── models/           # SQLAlchemy ORM models (User)
│   ├── schemas/          # Pydantic request/response schemas
│   ├── routers/          # auth.py, users.py
│   └── auth/             # JWT (bcrypt + python-jose), dependencies
├── tests/
│   ├── conftest.py       # DB table init fixture
│   └── test_auth.py      # 8 tests (register, login, auth, validation)
├── requirements.txt
├── .env.example
└── README.md
```

**Sample `main.py`:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_tables
from app.routers import auth, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
```

**Sample `auth/utils.py`:**
```python
import bcrypt
from jose import jwt, JWTError
from app.config import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(data: dict) -> str:
    ...
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
```
