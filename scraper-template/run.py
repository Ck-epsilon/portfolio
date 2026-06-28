"""
CLI entry point for the multi-site scraper.
Author: Ck.epsilon & Chaos (AI Programming Assistant)

Usage:
    python run.py --config sites/hackernews.yaml
    python run.py --config sites/hackernews.yaml --output results.json
"""

import argparse
import asyncio
import re
from pathlib import Path

import yaml

from scraper.engine import ScraperConfig, StealthScraper

_VALID_FORMATS = frozenset({"csv", "json", "excel"})


def _sanitize_name(name: str) -> str:
    """Remove path separators to prevent directory traversal."""
    return re.sub(r'[\\/]', '_', name)


def load_config(path: str) -> ScraperConfig:
    """Load scraper config from YAML, with validation."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    missing = [k for k in ("name", "start_urls", "selectors") if k not in raw]
    if missing:
        raise KeyError(f"Missing required config keys: {', '.join(missing)}")

    fmt = raw.get("output_format", "csv")
    if fmt not in _VALID_FORMATS:
        raise ValueError(
            f"Invalid output_format '{fmt}'. Must be one of: {', '.join(sorted(_VALID_FORMATS))}"
        )

    # Validate selectors are field names, not CSS selectors
    invalid = [k for k in raw["selectors"] if ">" in k or "<" in k]
    if invalid:
        raise ValueError(
            f"Selector keys must be field names, not CSS. "
            f"Found: {invalid}. Values: {' '.join(raw['selectors'].keys())}"
        )

    return ScraperConfig(
        name=raw["name"],
        start_urls=raw["start_urls"],
        selectors=raw["selectors"],
        pagination_selector=raw.get("pagination_selector"),
        max_pages=raw.get("max_pages", 10),
        delay_min=raw.get("delay_min", 1.0),
        delay_max=raw.get("delay_max", 3.0),
        max_retries=raw.get("max_retries", 3),
        retry_backoff=raw.get("retry_backoff", 2.0),
        output_format=fmt,
        login_url=raw.get("login_url"),
        login_selector=raw.get("login_selector"),
        login_credentials=raw.get("login_credentials"),
    )


async def main():
    parser = argparse.ArgumentParser(
        description="Multi-Site Web Scraper — Playwright + stealth mode"
    )
    parser.add_argument(
        "--config", "-c", required=True,
        help="Path to YAML config file (see sites/ for examples)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: output/<name>.<format>)"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    safe_name = _sanitize_name(config.name)
    output = args.output or f"output/{safe_name}.{config.output_format}"

    async with StealthScraper(config) as scraper:
        await scraper.run()
        scraper.save(output)


if __name__ == "__main__":
    asyncio.run(main())
