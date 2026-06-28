# AI Workbench — Multi-Agent Research Platform

CrewAI-powered research with LangFuse observability. Two agents (researcher + analyst) collaborate to research any topic and produce executive-ready reports.

Stack: `CrewAI` · `LangFuse` · `FastAPI` · `Docker`

## Quick Start

```bash
cp .env.example .env
# Fill in OPENAI_API_KEY and SERPER_API_KEY
docker compose up -d
```

Open **http://localhost** — enter a research topic, watch two agents at work.

## Architecture

```
┌──────────────┐
│  Frontend    │  ε-style single-file UI
│  Chat + WS   │  Nginx :80
└──────┬───────┘
       │ /api/* │ /ws/*
┌──────▼───────┐
│  Backend     │  FastAPI :8000
│  Crew Runner │  Background task execution
└──────┬───────┘
       │
┌──────▼───────┐
│  CrewAI      │  Two-agent crew
│  Researcher  │  Web search + source scraping
│  Analyst     │  Synthesis + report generation
└──────┬───────┘
       │ tracing
┌──────▼───────┐
│  LangFuse    │  LLM observability (optional)
│  Traces      │  Cost, latency, token usage
└──────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/research` | POST | Start a new research run |
| `/research` | GET | List all research runs |
| `/research/{id}` | GET | Get run status and result |
| `/ws/research/{id}` | WS | Real-time progress streaming |

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key (or compatible) |
| `LLM_MODEL` | No | Model name (default: gpt-4o-mini) |
| `SERPER_API_KEY` | Yes | Serper.dev API key for web search |
| `LANGFUSE_PUBLIC_KEY` | No | LangFuse public key for tracing |
| `LANGFUSE_SECRET_KEY` | No | LangFuse secret key |
| `LANGFUSE_HOST` | No | LangFuse host (default: cloud) |

## Example

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Current state of quantum computing in 2026"}'
```

The CrewAI team will:
1. **Researcher** searches the web, scrapes credible sources, extracts key facts
2. **Analyst** synthesizes findings into an executive report with top insights and recommendations

---

**Author:** Ck.epsilon & Chaos (AI Programming Assistant)
