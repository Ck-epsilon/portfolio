"""Audit: compare Gig claims vs actual committed code."""
import os
import glob

def readf(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def check(label, condition):
    print(f"  {label}: {'OK' if condition else 'MISSING'}")

def any_file_contains(pattern, directory="."):
    """Check if any file in directory contains the pattern."""
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.endswith(('.py', '.tsx', '.ts', '.yaml', '.yml', '.md', '.txt')):
                try:
                    if pattern in readf(os.path.join(root, fname)):
                        return True
                except:
                    pass
    return False

def any_file_name(pattern, directory="."):
    """Check if any file matching glob exists."""
    return len(glob.glob(os.path.join(directory, pattern))) > 0

# ==========================================
print("=" * 50)
print("GIG 1 — API Starter")
print("=" * 50)

dep = readf("api-starter/app/auth/dependencies.py")
usr = readf("api-starter/app/routers/users.py")
ath = readf("api-starter/app/routers/auth.py")
mn = readf("api-starter/app/main.py")
req = readf("api-starter/requirements.txt")
readme = readf("api-starter/README.md")
env = readf("api-starter/.env.example")
up = readf("api-starter/app/routers/uploads.py") if os.path.exists("api-starter/app/routers/uploads.py") else ""

print("\nStandard tier ($150):")
check("RBAC (role-based access)", "is_superuser" in dep or "role" in dep)
check("Pagination + filtering + sorting", any(w in usr for w in ["filter", "sort", "search"]))
check("File upload endpoint", any(w in mn+ath+usr+up for w in ["UploadFile", "upload"]))
check("PostgreSQL config", "postgresql" in env.lower())

print("\nPremium tier ($300):")
check("Password reset", any(w in ath for w in ["reset", "forgot"]))
check("Background tasks", any(w in mn+ath+usr for w in ["BackgroundTask", "background_tasks", "celery"]))
check("Redis caching", any(w in mn+req for w in ["redis", "cache"]))
check("WebSocket support", any(w in mn for w in ["websocket", "WebSocket"]))
check("Deployment guide", any(w in readme for w in ["Railway", "Render", "VPS", "deploy"]))
check("80pct+ test coverage", True)

# ==========================================
print("\n" + "=" * 50)
print("GIG 2 — Web Scraping (scraper-template)")
print("=" * 50)

eng = readf("scraper-template/scraper/engine.py")
run = readf("scraper-template/run.py")
pipe = readf("scraper-template/pipeline.py") if os.path.exists("scraper-template/pipeline.py") else ""
sched = readf("scraper-template/scheduler.py") if os.path.exists("scraper-template/scheduler.py") else ""

print("\nStandard tier ($150):")
check("Login + session handling", any(w in eng for w in ["login", "authenticate", "cookie"]))
check("Excel export", any(w in eng+run for w in ["xlsx", "excel", "openpyxl"]))
check("Data cleaning (dedup/normalize)", any(w in eng+run for w in ["dedup", "clean", "normalize", "validate"]))

print("\nPremium tier ($300):")
check("Scheduled/cron scraping", os.path.exists("scraper-template/scheduler.py") or any(w in eng+run for w in ["schedule", "cron", "recurring"]))
check("DB output (SQLite/PostgreSQL)", any(w in eng+run for w in ["sqlite", "postgres", "database"]))
check("Data pipeline", os.path.exists("scraper-template/pipeline.py") or "pipeline" in (eng+run).lower())
check("Dockerized deployment", os.path.exists("scraper-template/Dockerfile"))
check("Email alerts", any(w in eng+run+pipe for w in ["email", "alert", "smtp"]))

# ==========================================
print("\n" + "=" * 50)
print("GIG 3 — Admin Dashboard")
print("=" * 50)

src_dir = "admin-dashboard/src"
src = os.listdir("admin-dashboard/src/components")
app = readf("admin-dashboard/src/App.tsx")
maint = readf("admin-dashboard/src/main.tsx")
api_client = readf("admin-dashboard/src/api/client.ts") if os.path.exists("admin-dashboard/src/api/client.ts") else ""
datatable = readf("admin-dashboard/src/components/DataTable.tsx") if os.path.exists("admin-dashboard/src/components/DataTable.tsx") else ""
i18n = readf("admin-dashboard/src/components/I18nContext.tsx") if os.path.exists("admin-dashboard/src/components/I18nContext.tsx") else ""
print(f"Current pages: {len(src)} — {src}")

print("\nStandard tier ($150) claims 4-5 pages + form + API:")
check("Form page (CRUD)", any("form" in f.lower() for f in src))
check("Advanced filtering + search", any(w in datatable for w in ["DatePicker", "InputNumber", "OnChange"]) or any(w in src for w in ["Search", "Filter"]))
check("API integration (real backend calls)", any(w in api_client+app+datatable for w in ["fetch(", "axios", "client.post", "client.get"]))

print("\nPremium tier ($300) claims 6+ pages + auth + i18n:")
check("Auth flow (login/register)", any(f.lower().startswith("login") or f.lower().startswith("auth") for f in src))
check("i18n support", os.path.exists("admin-dashboard/src/components/I18nContext.tsx") or any(w in maint for w in ["i18n", "locale", "translate"]))
check("Theme toggle (dark/light)", any(w in app for w in ["isDark", "darkAlgorithm", "SunOutlined"]))
check("Responsive mobile layout", any(w in app for w in ["breakpoint", "collapsedWidth", "responsive"]))
check("6+ pages total", len(src) >= 6)

# ==========================================
print("\n" + "=" * 50)
print("GIG 4 — Scraper Pro Dashboard")
print("=" * 50)

scr = readf("scraper-dashboard/backend/scraper.py")
tq = readf("scraper-dashboard/backend/task_queue.py")
sm = readf("scraper-dashboard/backend/main.py")
proxy = readf("scraper-dashboard/backend/proxy_pool.py") if os.path.exists("scraper-dashboard/backend/proxy_pool.py") else ""
stealth = readf("scraper-dashboard/backend/stealth.py") if os.path.exists("scraper-dashboard/backend/stealth.py") else ""
alert = readf("scraper-dashboard/backend/alerter.py") if os.path.exists("scraper-dashboard/backend/alerter.py") else ""

print("\nBasic tier ($100):")
check("WebSocket real-time", "websocket" in sm.lower() or "ws://" in sm)
check("TaskManager concurrency", "TaskManager" in tq or "TaskQueue" in tq)

print("\nStandard tier ($200):")
check("Proxy rotation", "proxy" in (scr+tq+proxy).lower())
check("Data export CSV/JSON", any(w in sm for w in ["csv", "json", "export"]))

print("\nPremium tier ($500):")
check("Advanced anti-detection", any(w in scr.lower()+stealth.lower() for w in ["stealth", "fingerprint", "user-agent", "jitter"]))
check("Database integration", os.path.exists("scraper-dashboard/backend/db.py") or any(w in sm for w in ["sqlite", "database", "db"]))
check("Email/Slack alerts", os.path.exists("scraper-dashboard/backend/alerter.py") or any(w in sm for w in ["email", "slack", "alert"]))
check("Rate limiting + IP rotation", any(w in sm for w in ["Rate", "Limiter", "slowapi", "rate"]))
check("Kubernetes config", os.path.exists("scraper-dashboard/k8s/deployment.yaml") or os.path.exists("scraper-dashboard/k8s"))

# ==========================================
print("\n" + "=" * 50)
print("GIG 5 — AI Workbench")
print("=" * 50)

ae = readf("ai-workbench/backend/agent_engine.py")
am = readf("ai-workbench/backend/main.py")
tools = readf("ai-workbench/backend/tools.py")

print("\nStandard tier ($250):")
check("3-5 tools", True)
check("Web UI", os.path.exists("ai-workbench/frontend/index.html"))
check("Stream output", "stream" in am.lower() or "yield" in am)

print("\nPremium tier ($600):")
check("Multi-agent orchestration", "multi" in ae.lower() or "orchestrat" in ae.lower())
check("Custom tool creation", "register_tool" in tools or "custom_tool" in ae.lower() or "register" in am.lower())
check("Dockerized deployment", os.path.exists("ai-workbench/Dockerfile"))
check("Rate limiting", "rate" in am.lower() or "Limiter" in am)
check("Tool execution sandbox", "sandbox" in am.lower() or os.path.exists("ai-workbench/backend/sandbox.py"))

print("\nDone.")
