# Author: Ck.epsilon
"""
Stealth module: randomized headers, user-agent rotation, request jitter.
Integrates with proxy_pool for IP rotation.
"""

import random
import time

# Rotating User-Agent pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
]

# Accept-Language values
ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.8,zh-CN;q=0.6",
    "en-US,en;q=0.9,zh-CN;q=0.7,ja;q=0.5",
]

# Referer values for common LLM APIs
REFERERS = [
    "https://chat.openai.com/",
    "https://platform.openai.com/",
    "https://www.google.com/",
    "",
]


def random_headers(base_headers: dict | None = None) -> dict:
    """Generate randomized HTTP headers for API requests."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/event-stream, */*",
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": random.choice(REFERERS),
        "Sec-Ch-Ua": '"Chromium";v="125", "Not.A/Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": random.choice(['"Windows"', '"macOS"']),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "DNT": "1",
    }
    if base_headers:
        headers.update(base_headers)
    return headers


def jitter(base_delay: float = 1.0, factor: float = 0.5) -> float:
    """Apply random jitter: base_delay * (1 ± factor)."""
    return base_delay * (1 + random.uniform(-factor, factor))


def human_delay(min_ms: float = 200, max_ms: float = 800):
    """Sleep for a random human-like delay (blocking). Use before API calls."""
    time.sleep(random.uniform(min_ms, max_ms) / 1000)
