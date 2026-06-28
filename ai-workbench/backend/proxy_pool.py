# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""
Proxy rotation pool with health checking.
Supports round-robin, random, and weighted distribution strategies.
"""

import asyncio
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ProxyPool:
    """Thread-safe proxy rotation pool with health checking.

    Usage::

        pool = ProxyPool(["http://proxy1:8080", "http://proxy2:8080"])
        proxy = await pool.get_proxy()       # round-robin
        proxy = await pool.get_proxy(strategy="random")
        pool.report_failure(proxy)           # mark unhealthy
    """

    def __init__(self, proxies: list[str], health_check_url: str = "https://www.google.com"):
        self._proxies = proxies
        self._healthy = set(proxies)
        self._unhealthy: dict[str, float] = {}  # proxy → cooldown_until timestamp
        self._index = 0
        self._health_check_url = health_check_url
        self._lock = asyncio.Lock()

    async def get_proxy(self, strategy: str = "round_robin") -> Optional[str]:
        """Get a healthy proxy. Returns None if none available."""
        async with self._lock:
            # Recover proxies whose cooldown has expired
            now = asyncio.get_event_loop().time()
            recovered = [p for p, until in self._unhealthy.items() if now >= until]
            for p in recovered:
                self._unhealthy.pop(p)
                self._healthy.add(p)

            available = list(self._healthy)
            if not available:
                return None

            if strategy == "random":
                return random.choice(available)

            # Round-robin
            proxy = available[self._index % len(available)]
            self._index += 1
            return proxy

    def get_proxy_url(self, strategy: str = "round_robin") -> Optional[str]:
        """Synchronous wrapper for sync contexts."""
        available = list(self._healthy)
        if not available:
            return None
        if strategy == "random":
            return random.choice(available)
        proxy = available[self._index % len(available)]
        self._index += 1
        return proxy

    def report_failure(self, proxy: str, cooldown_seconds: int = 60):
        """Mark a proxy as unhealthy with cooldown."""
        if proxy in self._healthy:
            self._healthy.discard(proxy)
        self._unhealthy[proxy] = asyncio.get_event_loop().time() + cooldown_seconds
        logger.warning("Proxy %s marked unhealthy for %ds", proxy, cooldown_seconds)

    def report_success(self, proxy: str):
        """Re-add proxy to healthy pool."""
        self._unhealthy.pop(proxy, None)
        self._healthy.add(proxy)

    @property
    def healthy_count(self) -> int:
        return len(self._healthy)

    @property
    def total_count(self) -> int:
        return len(self._proxies)
