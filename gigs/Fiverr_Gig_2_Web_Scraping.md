# Fiverr Gig #2: Web Scraping & Data Pipeline

> **Author:** Ck.epsilon
> **Stack:** Python · Playwright · asyncio · CSV/JSON/Excel · SQLite/PostgreSQL · Docker
> **Portfolio:** [github.com/ck-epsilon](https://github.com/ck-epsilon) *(live previews available on request — portfolio growing weekly)*

## Gig 基本信息

| 字段 | 内容 |
|------|------|
| **Title** | Scrape any website, build your data pipeline (Python / Playwright) |
| **Category** | Programming & Tech → Data → Data Processing |
| **Service Type** | Web Scraping & Data Extraction |
| **Price Tiers** | Basic $80 / Standard $150 / Premium $300 |
| **Delivery Time** | 3 / 5 / 7 days |

## Gig Description

**I'll scrape websites that others can't — including login-gated and JavaScript-heavy pages.**

Need data from a website? I build robust scrapers that handle anti-bot measures, pagination, and dynamic content. Output delivered as clean CSV, JSON, Excel, or directly into your database. Built with Python + Playwright — the same stack used by serious data teams.

**What I scrape:**
- E-commerce: product listings, prices, reviews, stock levels
- Lead generation: business directories, contact info, company data
- Real estate: property listings, price history, rental data
- Job boards: listings, company profiles, salary data
- Any custom target — tell me the URL and what you need

**Anti-blocking built in:**
- Rotating user agents and headers
- Request throttling and delays
- Cookie/session management for login-gated pages
- Anti-detection measures (stealth headers, fingerprint masking, request throttling). Advanced CAPTCHA challenges (reCAPTCHA v3, hCaptcha, Cloudflare Turnstile) may require manual intervention or third-party solving services — I'll be upfront about what's feasible for your target.

**Why a custom scraper instead of an off-the-shelf tool (Octoparse, ParseHub)?**
- **No monthly subscription** — you pay once, run as long as the target site stays compatible. Octoparse Standard starts at $69/mo ($828/year). After 2 years you've spent $1,656 — and you still don't own the scraper logic.
- **Full source code** — modify field mappings, add new targets, tweak delays yourself.
- **Handles edge cases** — no-code tools break on dynamic layouts. My code adapts.

**What you need to provide:**
- Target URL(s) and the data fields you want extracted
- Login credentials if the site requires authentication (test account preferred)
- Output format preference (CSV/JSON/Excel/DB)

---

## Price Tiers

### Basic ($80) — 3 Days · ⭐ Quick Extraction
- 1 target website
- Up to 500 records
- Simple HTML scraping (no login required)
- Output: CSV or JSON
- Single-run script

### Standard ($150) — 5 Days · 🔥 Best for Business Data
- 1-2 target websites
- Up to 5,000 records
- Login + session handling
- JavaScript-rendered pages (Playwright)
- Pagination handling
- Output: CSV, JSON, or Excel
- Data cleaning (dedup, normalize, validate)
- Configurable via `.env` or CLI args

### Premium ($300) — 7 Days · 🚀 Full Pipeline
- 3+ target websites or continuous scraping
- Unlimited records (rate-limited to respect target servers)
- Full anti-detection: rotating proxies, fingerprint spoofing
- Scheduled/cron scraping script
- Database output: SQLite, PostgreSQL, or MySQL
- Data pipeline: scrape → clean → transform → store
- Dockerized deployment
- Error logging + retry logic + email alerts on failure
- README + runbook

---

## FAQ

**Q: What sites can you scrape?**
A: Most public websites. For sites requiring login, I need test credentials. I do NOT scrape sites that are illegal to scrape (no banking, no government-restricted data).

**Q: Can you scrape behind a login?**
A: Yes — Playwright can handle login flows, 2FA screens, and session cookies. Provide test credentials.

**Q: What if the site blocks me?**
A: The Standard and Premium tiers include anti-detection measures. For aggressive anti-bot systems (Cloudflare Turnstile, DataDome), additional work may be needed — message me first.

**Q: What if the website changes its layout after delivery?**
A: Standard and Premium tiers include a 7-day post-delivery maintenance window for layout-change fixes. Response within 24 hours on business days. After 7 days, layout updates available at $30/site. Note: I cannot guarantee a scraper will work indefinitely — major site redesigns (full URL/architecture changes) may require a new scope.

**Q: Can you set up recurring scraping?**
A: Premium tier includes cron scheduling. The script can run daily, weekly, or hourly on your server.

**Q: What happens after delivery?**
A: You get the full source code + run instructions. Standard/Premium include 7 days of post-delivery support. Need ongoing maintenance? Message me for a retainer.

**Q: Is this legal?**
A: I scrape publicly accessible data only. You are responsible for complying with the target site's robots.txt and Terms of Service. I will not scrape any site where scraping is explicitly prohibited by law.

---

## Code Template (Deliverable Preview)

```
project/
├── scraper/
│   ├── __init__.py
│   ├── main.py            # Entry point + CLI
│   ├── config.py          # URLs, delays, credentials
│   ├── browser.py         # Playwright setup + anti-detection
│   ├── extractors/        # Per-site extractor modules
│   │   └── target_site.py
│   ├── cleaners/          # Data cleaning pipeline
│   ├── exporters/         # CSV, JSON, Excel, DB writers
│   └── utils.py           # Rate limiting, retries, logging
├── output/                # Scraped data goes here
├── logs/                  # Run logs
├── requirements.txt
├── .env.example
└── README.md
```

**Sample `main.py`:**
```python
import asyncio
import argparse
from scraper.config import TARGETS
from scraper.browser import get_browser_page
from scraper.extractors import TargetSiteExtractor
from scraper.exporters import CSVExporter, JSONExporter

async def scrape_target(name, config):
    page = await get_browser_page()
    extractor = TargetSiteExtractor(page, config)
    
    results = []
    async for record in extractor.paginate():
        results.append(record)
    
    await page.close()
    return results

async def main(target_name=None):
    targets = {target_name: TARGETS[target_name]} if target_name else TARGETS
    
    for name, config in targets.items():
        print(f"Scraping {name}...")
        data = await scrape_target(name, config)
        
        CSVExporter.save(data, f"output/{name}.csv")
        JSONExporter.save(data, f"output/{name}.json")
        print(f"  → {len(data)} records saved")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="Specific target to scrape")
    args = parser.parse_args()
    asyncio.run(main(args.target))
```
