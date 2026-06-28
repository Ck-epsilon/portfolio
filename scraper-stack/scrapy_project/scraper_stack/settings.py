# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Scrapy project settings for scraper-stack.

Production defaults tuned for reliability over speed.
Override per-spider or per-environment via environment variables.
"""

import os

BOT_NAME = "scraper_stack"
SPIDER_MODULES = ["scraper_stack.spiders"]
NEWSPIDER_MODULE = "scraper_stack.spiders"

# ── Politeness ──────────────────────────────────────────────────────
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = float(os.getenv("DOWNLOAD_DELAY", "1.5"))
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", "8"))
CONCURRENT_REQUESTS_PER_DOMAIN = int(os.getenv("CONCURRENT_REQUESTS_PER_DOMAIN", "2"))

# ── Auto-throttle (adaptive rate limiting) ─────────────────────────
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2.0
AUTOTHROTTLE_MAX_DELAY = 30.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# ── Retry ───────────────────────────────────────────────────────────
RETRY_ENABLED = True
RETRY_TIMES = int(os.getenv("RETRY_TIMES", "3"))
RETRY_HTTP_CODES = [429, 500, 502, 503, 504, 408]

# ── Middleware ──────────────────────────────────────────────────────
DOWNLOADER_MIDDLEWARES = {
    "scraper_stack.middlewares.StealthUserAgentMiddleware": 400,
    "scraper_stack.middlewares.ProxyRotationMiddleware": 450,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 500,
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 750,
}

# Playwright integration (opt-in per spider via meta key)
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# ── Pipelines ───────────────────────────────────────────────────────
ITEM_PIPELINES = {
    "scraper_stack.pipelines.ValidationPipeline": 100,
    "scraper_stack.pipelines.CSVInjectionGuardPipeline": 200,
    "scraper_stack.pipelines.DuplicateFilterPipeline": 300,
    "scraper_stack.pipelines.MultiFormatExportPipeline": 400,
}

# ── Logging ─────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# ── Export ──────────────────────────────────────────────────────────
FEED_EXPORT_ENCODING = "utf-8"
FEED_EXPORT_INDENT = 2

# ── Cookies / Sessions ──────────────────────────────────────────────
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# ── Extensions ──────────────────────────────────────────────────────
EXTENSIONS = {
    "scrapy.extensions.closespider.CloseSpider": 100,
    "scrapy.extensions.logstats.LogStats": 200,
}
CLOSESPIDER_ITEMCOUNT = int(os.getenv("CLOSESPIDER_ITEMCOUNT", "0"))
CLOSESPIDER_TIMEOUT = int(os.getenv("CLOSESPIDER_TIMEOUT", "0"))

# ── Telnet (expose for Scrapyd monitoring) ──────────────────────────
TELNETCONSOLE_ENABLED = True
TELNETCONSOLE_PORT = [6023, 6073]
