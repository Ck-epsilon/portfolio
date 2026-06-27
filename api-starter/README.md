# FastAPI Starter — Production-Ready Scaffold / 生产级脚手架

[English](#english) | [中文](#中文)

---

## English

### Supported Environment

| Software | Required | Tested |
|----------|----------|--------|
| Python | 3.10+ | 3.10.20 ✅ |
| FastAPI | 0.100+ | ✅ |
| SQLAlchemy | 2.0+ | ✅ |
| Pydantic | 2.0+ | ✅ |
| Uvicorn | 0.23+ | ✅ |

### Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for interactive Swagger docs.

**→ [Open Live Preview](preview.html)** — zero-dependency interactive demo

### Project Structure

```
api-starter/
├── app/
│   ├── main.py          # App entry point, CORS, health check
│   ├── config.py        # Environment-based settings
│   ├── database.py      # Async SQLAlchemy engine + sessions
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   └── routers/         # API route handlers
├── tests/               # pytest test suite
├── screenshots/         # Demo screenshots
├── requirements.txt
└── README.md
```

### Features

- FastAPI with full async support
- Automatic OpenAPI / Swagger UI
- CORS middleware pre-configured
- SQLAlchemy 2.0 async (PostgreSQL/SQLite)
- JWT authentication (login, refresh, logout)
- Pydantic v2 request validation
- Health check endpoint
- Docker-ready

### Screenshot

![API Starter Swagger](./screenshots/api-starter.png)

---

## 中文

### 支持环境

| 软件 | 要求版本 | 实测 |
|------|---------|------|
| Python | 3.10+ | 3.10.20 ✅ |
| FastAPI | 0.100+ | ✅ |
| SQLAlchemy | 2.0+ | ✅ |
| Pydantic | 2.0+ | ✅ |
| Uvicorn | 0.23+ | ✅ |

### 快速启动

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看交互式 API 文档。

### 项目结构

```
api-starter/
├── app/
│   ├── main.py          # 入口 + CORS + 健康检查
│   ├── config.py        # 环境变量配置
│   ├── database.py      # 异步 SQLAlchemy 引擎
│   ├── models/          # ORM 数据模型
│   ├── schemas/         # Pydantic 请求/响应模型
│   └── routers/         # API 路由
├── tests/               # pytest 测试
├── screenshots/         # 演示截图
├── requirements.txt
└── README.md
```

### 功能

- FastAPI 全异步支持
- 自动生成 OpenAPI / Swagger 文档
- CORS 中间件预配置
- SQLAlchemy 2.0 异步 (PostgreSQL/SQLite)
- JWT 认证 (登录/刷新/登出)
- Pydantic v2 请求校验
- 健康检查端点
- 可 Docker 部署
