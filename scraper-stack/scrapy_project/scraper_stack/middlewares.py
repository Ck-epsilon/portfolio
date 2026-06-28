# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Scrapy downloader middlewares: stealth, proxy rotation, anti-detection."""

import logging
import random
import os

logger = logging.getLogger(__name__)

# Default rotating User-Agent pool (modern browsers, updated 2026)
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/18.2 Safari/605.1.15",
]


class StealthUserAgentMiddleware:
    """Rotate User-Agent header on every request.

    Configurable via environment:
        UA_POOL: comma-separated list of User-Agent strings
    """

    def __init__(self):
        custom_ua = os.getenv("UA_POOL", "")
        if custom_ua:
            self._pool = [ua.strip() for ua in custom_ua.split(",") if ua.strip()]
        else:
            self._pool = _USER_AGENTS

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        ua = random.choice(self._pool)
        request.headers.setdefault("User-Agent", ua)
        request.headers.setdefault("Accept-Language", "en-US,en;q=0.9")
        request.headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")


class ProxyRotationMiddleware:
    """Rotate HTTP proxies from a pool.

    Proxy pool configured via environment:
        PROXY_LIST: comma-separated http://user:pass@host:port URLs
        PROXY_MODE: "random" (default) or "round_robin"

    For production, integrate with a proxy rotation service (BrightData, Oxylabs, etc.)
    """

    def __init__(self):
        proxy_env = os.getenv("PROXY_LIST", "")
        self._proxies: list[str] = [p.strip() for p in proxy_env.split(",") if p.strip()]
        self._mode = os.getenv("PROXY_MODE", "random")
        self._rr_index = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_request(self, request, spider):
        if not self._proxies:
            return

        if self._mode == "round_robin":
            proxy = self._proxies[self._rr_index % len(self._proxies)]
            self._rr_index += 1
        else:
            proxy = random.choice(self._proxies)

        request.meta["proxy"] = proxy
        logger.debug("Using proxy: %s", proxy.split("@")[-1] if "@" in proxy else proxy)
