# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Generic configurable spider — driven by YAML config files.

Supports:
- Static HTML scraping (default, fast)
- JavaScript rendering via Playwright (opt-in with ``js_render: true``)
- Pagination (CSS selector for "next page" button)
- Login flows (multi-step form submission)
- Custom item schema validation
"""

import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import scrapy
import yaml
from scrapy.http import Response

logger = logging.getLogger(__name__)


class GenericSpider(scrapy.Spider):
    """Config-driven spider — define target, selectors, and output in YAML.

    Config file structure::

        name: example_spider
        start_urls:
          - https://example.com/page/1
        selectors:
          title: h1.product-title::text
          price: span.price::text
          link: a.product-link::attr(href)
        pagination_selector: a.next-page::attr(href)
        max_pages: 5
        js_render: false
        login:
          url: https://example.com/login
          username_selector: input[name="email"]
          password_selector: input[name="password"]
          submit_selector: button[type="submit"]
          credentials:
            username: "${LOGIN_USER}"
            password: "${LOGIN_PASS}"
        output:
          formats: [csv, json]
          dir: output/
    """

    name = "generic"

    def __init__(self, config_path: str = "", config: dict | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if config:
            self._cfg = config
        elif config_path:
            self._cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
        else:
            raise ValueError("Either config_path or config dict is required")

        self._resolve_env_vars()
        self._validate_config()
        self._apply_config()

    def _resolve_env_vars(self) -> None:
        """Replace ``${ENV_VAR}`` placeholders with environment values."""

        def _resolve(obj: Any) -> Any:
            if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
                return os.getenv(obj[2:-1], obj)
            if isinstance(obj, dict):
                return {k: _resolve(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_resolve(v) for v in obj]
            return obj

        self._cfg = _resolve(self._cfg)

    def _validate_config(self) -> None:
        required = ["start_urls", "selectors"]
        missing = [k for k in required if k not in self._cfg]
        if missing:
            raise KeyError(f"Missing required config keys: {missing}")

    def _apply_config(self) -> None:
        # Override spider name if provided
        if "name" in self._cfg:
            self.name = self._cfg["name"]

        self.start_urls = self._cfg["start_urls"]
        self.selectors: dict[str, str] = self._cfg["selectors"]
        self.pagination_selector: str = self._cfg.get("pagination_selector", "")
        self.max_pages: int = self._cfg.get("max_pages", 10)
        self.js_render: bool = self._cfg.get("js_render", False)
        self.login_config: dict = self._cfg.get("login", {})
        self._page_count: int = 0

        # Export settings
        output_cfg = self._cfg.get("output", {})
        self.output_dir: str = output_cfg.get("dir", "output/")
        self.output_formats: list[str] = output_cfg.get("formats", ["csv", "json"])

    def start_requests(self):
        """If login is configured, start with login flow; otherwise scrape directly."""
        if self.login_config:
            login_url = self.login_config.get("url", "")
            if login_url:
                logger.info("Starting login flow: %s", login_url)
                yield scrapy.Request(
                    login_url,
                    callback=self._login,
                    meta={"playwright": self.js_render} if self.js_render else {},
                )
                return

        for url in self.start_urls:
            yield self._make_request(url)

    def _make_request(self, url: str, callback=None):
        """Create a request, optionally enabling Playwright for JS rendering."""
        meta = {}
        if self.js_render:
            meta["playwright"] = True
            meta["playwright_include_page"] = True
        return scrapy.Request(url, callback=callback or self.parse, meta=meta)

    async def _login(self, response: Response):
        """Handle login flow with Playwright for form submission."""
        credentials = self.login_config.get("credentials", {})

        if not self.js_render:
            # Static login: extract form field names from CSS selectors
            def _extract_field_name(selector: str, default: str) -> str:
                """Extract the ``name`` attribute from a CSS selector like
                ``input[name="email"]``. Returns *default* if extraction fails."""
                m = re.search(r'\[name=["\']?([^"\'\] ]+)', selector)
                return m.group(1) if m else default

            formdata = {
                _extract_field_name(
                    self.login_config.get("username_selector", "input[name=username]"),
                    "username",
                ): credentials.get("username", ""),
                _extract_field_name(
                    self.login_config.get("password_selector", "input[name=password]"),
                    "password",
                ): credentials.get("password", ""),
            }
            yield scrapy.FormRequest.from_response(
                response,
                formdata=formdata,
                callback=self._after_login,
            )
        else:
            # Playwright login: submit form in real browser
            page = response.meta.get("playwright_page")
            if page:
                await page.fill(
                    self.login_config.get("username_selector", "input[name=email]"),
                    self.login_config.get("credentials", {}).get("username", ""),
                )
                await page.fill(
                    self.login_config.get("password_selector", "input[name=password]"),
                    self.login_config.get("credentials", {}).get("password", ""),
                )
                await page.click(self.login_config.get("submit_selector", "button[type=submit]"))
                await page.wait_for_load_state("networkidle")
                # After login, navigate to start URLs
                for url in self.start_urls:
                    yield self._make_request(url)

    def _after_login(self, response: Response):
        """After login, start scraping target URLs."""
        for url in self.start_urls:
            yield self._make_request(url)

    def parse(self, response: Response):
        """Extract items from the current page."""
        self._page_count += 1
        logger.info("Parsing page %d/%d: %s", self._page_count, self.max_pages, response.url)

        # Extract items matching the configured selectors
        items = response.css(self._cfg.get("item_selector", "body"))
        if not items:
            # No item container — each selector matches its own elements
            items = [response]

        for container in items:
            item = {
                "url": response.url,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "_schema": self.selectors,
            }
            for field, sel in self.selectors.items():
                # Support ::text and ::attr(href) suffixes
                if "::attr(" in sel:
                    sel_base, attr = sel.split("::attr(", 1)
                    attr = attr.rstrip(")")
                    value = container.css(sel_base).attrib.get(attr, "")
                elif sel.endswith("::text"):
                    sel_base = sel.rsplit("::text", 1)[0]
                    value = container.css(sel_base + "::text").get(default="").strip()
                else:
                    value = container.css(sel + "::text").get(default="").strip()
                item[field] = value

            yield item

        # Pagination
        if self._page_count < self.max_pages and self.pagination_selector:
            next_url = response.css(self.pagination_selector).get()
            if next_url:
                yield self._make_request(response.urljoin(next_url))
            else:
                logger.info("No next page found — stopping pagination")
