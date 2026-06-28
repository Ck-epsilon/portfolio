# Fiverr Gig #4: Scraper Pro — Real-Time Web Scraping Dashboard

> **Author:** Ck.epsilon
> **Stack:** Python · FastAPI · Playwright · WebSocket · asyncio · Docker · Nginx
> **Portfolio:** [github.com/ck-epsilon](https://github.com/ck-epsilon) *(live previews available on request — portfolio growing weekly)*
> **See it in action:** Live demo available on request — contact me for a walkthrough.

## Gig 基本信息

| 字段 | 内容 |
|------|------|
| **Title** | Build a real-time web scraping dashboard with live monitoring |
| **Category** | Programming & Tech → Data Processing → Web Scraping |
| **Service Type** | Custom Web Scraping Platform |
| **Price Tiers** | Basic $100 / Standard $200 / Premium $500 |
| **Delivery Time** | 3 / 5 / 10 days |

## Gig Description

**I'll build your real-time web scraping dashboard — live progress, instant logs, and one-click CSV export.**

Need more than a script? This is a complete scraping platform: async task queue, WebSocket live streaming, Playwright-powered extraction, and a clean dashboard to monitor everything in real time. Configurable concurrency (tested at 50 tasks on i7-12700H, 32 GB RAM). You see every scrape as it happens — progress bars, live logs, instant results.

**What you get:**
- Web dashboard with live progress bars and real-time log stream
- Async task queue (FIFO, configurable concurrency)
- Playwright headless Chromium engine with CSS selector extraction
- WebSocket streaming — typed log events (info/warn/error/progress/complete)
- Structured field extraction from any HTML (JSON-defined schemas)
- CSV export — one-click download of all results
- Searchable results table with filtering
- Docker Compose for single-command deployment (`docker compose up`)

**Why this instead of Apify / Bright Data / scraping-as-a-service?**
- **No recurring compute costs** — Apify and Bright Data charge per Compute Unit (CU) or per successful request. At scale, monthly bills add up fast. Here: pay once, run unlimited on your own hardware.
- **You own the platform** — not locked into a vendor's infrastructure. Deploy on your own server. No API deprecation risk, no pricing surprises.
- **Full visibility** — see every log, every error, every retry in real time via WebSocket. No black-box "we'll email you when it's done."

**What you need to provide:**
- Target URL(s) and the data fields to extract (CSS selectors or descriptions)
- Login credentials if the site requires authentication (test account)
- Server specs if you need a deployment guide (Premium tier)

**Not sure what you need?** Message me first. I'll help you scope it in 1-2 questions.

---

## Price Tiers

### Basic ($100) — 3 Days · ⭐ Starter Platform
- Single-site scraper with dashboard
- 1-3 extraction fields (title, price, link etc.)
- Playwright engine with CSS selectors
- Real-time log streaming via WebSocket
- Results table with search
- CSV export
- README with setup instructions

### Standard ($200) — 5 Days · 🔥 Multi-Site Power
- 3-10 extraction fields with structured JSON schemas
- 10+ concurrent task queue
- Pagination support (multi-page scraping)
- Custom log event types
- Progress tracking with ETA
- Docker + docker-compose
- Error recovery (retry on failure)

### Premium ($500) — 10 Days · 🚀 Enterprise Platform
- 50+ concurrent tasks
- Multi-site scraping with site-specific configs
- Anti-detection headers and stealth delays
- Database integration (PostgreSQL for persistent results)
- Scheduled scraping (cron-style)
- Custom dashboard branding (your logo/colors)
- API authentication for your team
- CI/CD pipeline (GitHub Actions)
- Deployment guide to your server or cloud

---

## FAQ

**Q: What does the dashboard look like?**
A: Clean single-page web app — task list on the left (with progress bars), live log stream in the center, results table below. Everything updates in real time via WebSocket. Contact me for a live demo link.

**Q: Can it handle sites with JavaScript-rendered content?**
A: Yes. Playwright runs a real Chromium browser, so SPAs, infinite scroll, and JS-heavy sites work.

**Q: What about anti-bot protection (Cloudflare, DataDome)?**
A: I include standard stealth headers and delays. Premium tier adds rotating user agents. Advanced challenges like Cloudflare Turnstile or hCaptcha may need additional handling — message me to discuss.

**Q: Can you scrape behind a login?**
A: Yes, Playwright can handle login flows. But I only work with sites where you have authorized access.

**Q: Is this legal?**
A: The tool is designed for publicly accessible data. You're responsible for complying with the target site's robots.txt and ToS.

**Q: Can I customize the dashboard appearance?**
A: Basic/Standard use a clean default design (dark theme). Premium includes branding customization (logo, colors).

**Q: What happens after delivery?**
A: You get the full source code. Standard/Premium include 7 days of post-delivery bug-fix support. Docker Compose means you deploy with one command. Need ongoing maintenance? Message me.

**Q: How does this differ from your Web Scraping Gig (#2)?**
A: Gig #2 is a **script** — you run it, it outputs a CSV. This Gig is a **platform** — a live dashboard with task queue, WebSocket streaming, and multi-user capability. Pick Gig #2 if you need one-time extraction. Pick this if you need ongoing scraping with monitoring.

---

## Code Template (Deliverable Preview)

```
scraper-dashboard/
├── backend/
│   ├── main.py           # FastAPI app + WebSocket + REST API
│   ├── scraper.py        # Playwright scraping engine
│   ├── task_queue.py     # TaskManager — async task queue
│   └── requirements.txt
├── frontend/
│   └── index.html        # Single-file dashboard (zero dependencies)
├── docker-compose.yml    # Backend + Nginx frontend
├── Dockerfile
└── README.md
```

**Sample `main.py` (API entry point):**
```python
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from task_queue import TaskManager, TaskStatus
from scraper import scrape_task
import asyncio

app = FastAPI(title="Scraper Pro", version="1.0.0", docs_url="/docs")
task_manager = TaskManager(max_concurrency=2)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

@app.post("/tasks")
async def create_task(payload: dict):
    task = task_manager.create_task(payload.get("url", ""), payload.get("config", {}))
    asyncio.create_task(scrape_task(task))
    return {"task_id": task.id, "status": task.status.value}

@app.get("/tasks")
async def list_tasks():
    return [t.to_dict() for t in task_manager.list_all()]

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = task_manager.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()

@app.websocket("/ws/{task_id}")
async def stream_logs(ws: WebSocket, task_id: str):
    await ws.accept()
    task = task_manager.get(task_id)
    if not task:
        await ws.close(code=4004)
        return
    try:
        while True:
            try:
                event = await asyncio.wait_for(task.log_queue.get(), timeout=1.0)
                await ws.send_json(event)
            except asyncio.TimeoutError:
                if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                    break
    except WebSocketDisconnect:
        pass

@app.get("/tasks/{task_id}/export")
async def export_csv(task_id: str):
    task = task_manager.get(task_id)
    if not task:
        raise HTTPException(status_code=404)
    # Returns CSV streaming response
    ...

@app.get("/health")
async def health():
    return {"status": "ok", "queue_size": len(task_manager.list_all())}
```
