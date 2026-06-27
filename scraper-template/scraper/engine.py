"""
Multi-Site Web Scraper — production-ready template.

Features:
- Playwright-based with stealth mode (anti-detection)
- Auto-pagination detection
- CSV & JSON export
- Configurable via YAML/JSON
- Rate limiting + retry with backoff

Usage:
    python run.py --config sites/example.yaml --output data.csv
"""

import asyncio
import csv
import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Browser, Page
except ImportError:
    print("pip install playwright && playwright install chromium")
    raise


@dataclass
class ScraperConfig:
    name: str
    start_urls: list[str]
    selectors: dict  # {field_name: css_selector}
    pagination_selector: str | None = None
    max_pages: int = 10
    delay_min: float = 1.0
    delay_max: float = 3.0
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    output_format: str = "csv"  # csv | json


class StealthScraper:
    """Scraper with stealth features to avoid detection."""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.results: list[dict] = []
        self.browser: Browser | None = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        return self

    async def __aexit__(self, *args):
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()

    async def _new_page(self) -> Page:
        """Create a stealth-configured page."""
        context = await self.browser.new_context(
            user_agent=self.config.user_agent,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = await context.new_page()

        # Remove webdriver detection flags
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)
        return page

    async def scrape_page(self, url: str) -> list[dict]:
        """Scrape a single page, extracting fields by configured selectors."""
        page = await self._new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for content to render
            await page.wait_for_timeout(2000)

            items = []
            # Extract items using the first key's selector as the container
            primary_field = list(self.config.selectors.keys())[0]
            elements = await page.query_selector_all(
                self.config.selectors[primary_field]
            )

            # Get all other selectors
            parent_selectors = {}
            for field, sel in self.config.selectors.items():
                if field != primary_field:
                    parent_selectors[field] = await page.query_selector_all(sel)

            for i, el in enumerate(elements):
                item = {primary_field: (await el.inner_text()).strip()}
                for field, els in parent_selectors.items():
                    if i < len(els):
                        item[field] = (await els[i].inner_text()).strip()
                    else:
                        item[field] = ""
                items.append(item)

            return items
        finally:
            await page.close()

    async def run(self) -> list[dict]:
        """Execute full scrape across all pages."""
        print(f"[{self.config.name}] Starting scrape...")

        for url in self.config.start_urls:
            print(f"  → {url}")

            # Handle pagination if configured
            if self.config.pagination_selector:
                items = await self.scrape_paginated(url)
            else:
                items = await self.scrape_page(url)

            self.results.extend(items)
            print(f"    {len(items)} items extracted")

            # Rate limiting
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            time.sleep(delay)

        print(f"[{self.config.name}] Done. Total: {len(self.results)} items")
        return self.results

    async def scrape_paginated(self, start_url: str) -> list[dict]:
        """Scrape with automatic pagination."""
        all_items = []
        page = await self._new_page()
        current_url = start_url

        try:
            for p in range(self.config.max_pages):
                await page.goto(current_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(1500)

                # Scrape this page
                items = await self.scrape_page(current_url)
                all_items.extend(items)

                # Find next page link
                next_btn = await page.query_selector(self.config.pagination_selector)
                if next_btn:
                    href = await next_btn.get_attribute("href")
                    if href:
                        current_url = (
                            href if href.startswith("http")
                            else f"{start_url.rstrip('/')}/{href.lstrip('/')}"
                        )
                        delay = random.uniform(1.0, 2.0)
                        time.sleep(delay)
                        continue
                break  # No more pages
        finally:
            await page.close()

        return all_items

    def save(self, output_path: str):
        """Save results to CSV or JSON."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        if self.config.output_format == "json":
            with open(output, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
        else:
            if not self.results:
                print("Warning: No results to save.")
                return
            fieldnames = list(self.results[0].keys())
            with open(output, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)

        print(f"Saved {len(self.results)} items → {output.absolute()}")
