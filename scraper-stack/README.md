# Scraper Stack

**Production-grade web scraping platform.** Scrapy + Playwright + Scrapyd + real-time dashboard.

Stack: `Scrapy 2.13+` · `Playwright` · `Scrapyd` · `FastAPI` · `Docker`

---

## Quick Start

```bash
git clone https://github.com/Ck-epsilon/portfolio.git
cd portfolio/scraper-stack
docker compose up -d
```

Then open **http://localhost** — configure a target site, hit "Run", watch live logs.

---

## Architecture

```
                     ┌──────────────┐
                     │   Frontend   │  Nginx :80
                     │  Dashboard   │  Single-file HTML, ε style
                     └──────┬───────┘
                            │ /api/*  │ /ws/*
                     ┌──────▼───────┐
                     │   Backend    │  FastAPI :8000
                     │  REST + WS   │  Scrapyd HTTP client
                     └──────┬───────┘
                            │ HTTP API
                     ┌──────▼───────┐
                     │   Scrapyd    │  :6800
                     │  Spider Pool │  FIFO queue, auto-retry
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │   Scrapy     │  Engine
                     │  + Playwright│  Downloader → Pipelines
                     └──────────────┘
```

## Features

| Layer | Feature | Status |
|-------|---------|--------|
| **Core Engine** | Scrapy (industry standard, 50k+ stars) | ✅ |
| | Playwright — real Chromium for JS rendering | ✅ |
| **Reliability** | Auto-throttle (adaptive rate limiting) | ✅ |
| | Exponential backoff retry (3×) | ✅ |
| | robots.txt compliance | ✅ |
| **Anti-detection** | Rotating User-Agent pool (5 browsers) | ✅ |
| | Stealth headers (Accept-Language, Accept) | ✅ |
| | Proxy rotation (random / round-robin) | ✅ |
| **Scheduling** | Scrapyd daemon (HTTP API) | ✅ |
| | Job queue with FIFO | ✅ |
| | Cancel running jobs | ✅ |
| **Dashboard** | Live WebSocket log streaming | ✅ |
| | Config browser (YAML → UI cards) | ✅ |
| | Job status table (pending/running/finished) | ✅ |
| | One-click CSV/JSON export | ✅ |
| **Data Quality** | Pydantic schema validation per item | ✅ |
| | CSV injection guard | ✅ |
| | Duplicate filtering (SHA-256 hash) | ✅ |
| **Deployment** | Docker Compose (3 services, 1 command) | ✅ |
| | Nginx reverse proxy (dashboard → API) | ✅ |
| | Health checks (Scrapyd daemonstatus.json) | ✅ |

## Usage

### 1. Define your target

Create a YAML config in `configs/`:

```yaml
name: hackernews
start_urls:
  - https://news.ycombinator.com/
selectors:
  title: span.titleline > a::text
  link: span.titleline > a::attr(href)
  score: span.score::text
pagination_selector: "a.morelink::attr(href)"
max_pages: 3

output:
  formats: [csv, json]
  dir: output/
```

### 2. Run from the dashboard

Open **http://localhost** → click **"Run Scraper"** on your config card.

### 3. Or run via CLI

```bash
# Direct Scrapy run (development)
cd scrapy_project
scrapy crawl generic -a config_path=../configs/hackernews.yaml

# Or via Scrapyd API
curl http://localhost:6800/schedule.json \
  -d project=scraper_stack \
  -d spider=generic \
  -d setting=CONFIG_NAME=hackernews
```

### 4. Monitor & export

- Dashboard shows live logs via WebSocket
- Click **Export** on a finished job → CSV + JSON download

## JavaScript Rendering

For SPAs and JS-heavy sites, enable Playwright:

```yaml
js_render: true
# Optional: wait for a specific element before scraping
wait_selector: ".product-grid.loaded"
```

The spider launches a headless Chromium browser per request. Scrapy's auto-throttle limits concurrency to avoid overloading the target.

## Login-Flow Scraping

```yaml
login:
  url: https://example.com/login
  username_selector: input[name="email"]
  password_selector: input[name="password"]
  submit_selector: button[type="submit"]
  credentials:
    username: "${LOGIN_USER}"
    password: "${LOGIN_PASS}"
```

Set `LOGIN_USER` and `LOGIN_PASS` as environment variables in `docker-compose.yml` or your `.env` file.

## Proxy Rotation

```bash
# In docker-compose.yml environment:
PROXY_LIST=http://user:pass@proxy1:8080,http://user:pass@proxy2:8080
PROXY_MODE=random  # or "round_robin"
```

For production, integrate with a proxy service (BrightData, Oxylabs, Smartproxy).

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health (backend + Scrapyd) |
| `/configs` | GET | List available YAML configs |
| `/jobs` | POST | Schedule a new scrape job |
| `/jobs` | GET | List all jobs grouped by status |
| `/jobs/{id}` | GET | Get single job status |
| `/jobs/{id}/cancel` | POST | Cancel a running/pending job |
| `/jobs/{id}/export` | GET | Download results (CSV/JSON) |
| `/ws/{id}` | WS | Live log streaming |

## FAQ

**Why Scrapy instead of custom httpx/BS4?**
Scrapy is the industry standard (50k+ GitHub stars). It brings built-in dedup, retry, middleware, auto-throttle, and a mature pipeline system — all of which you'd have to build yourself with raw httpx.

**Can it handle JavaScript-heavy sites?**
Yes. Set `js_render: true` in your config. The spider uses Playwright (real Chromium) to render SPAs, infinite scroll, and JS-heavy pages.

**What about anti-bot protection?**
Standard stealth measures are built in: rotating User-Agent, stealth headers, configurable delays, and proxy rotation. For aggressive challenges (Cloudflare Turnstile, DataDome), additional handling may be needed.

**How do I schedule recurring scrapes?**
Scrapyd doesn't have built-in cron. Add a cron job on your host:

```bash
# Scrape every 6 hours
0 */6 * * * curl -X POST http://localhost:6800/schedule.json \
  -d project=scraper_stack -d spider=generic \
  -d setting=CONFIG_NAME=hackernews
```

**Do I own the source code?**
Yes. This is a template you customize. No subscription, no platform lock-in.

## Security

| CVE | Severity | Mitigation |
|-----|----------|------------|
| CVE-2025-6176 | 7.5 High | Scrapy >= 2.13.3 + brotli >= 1.2.0 |
| CVE-2024-3574 | 6.5 Medium | Fixed in latest Scrapy |
| CVE-2024-1892 | 5.3 Medium | Scrapyd behind reverse proxy |

See `运营/framework_security_audit.md` in the parent repo for the full audit.

---

**Author:** Ck.epsilon & Chaos (AI Programming Assistant)
**License:** MIT
