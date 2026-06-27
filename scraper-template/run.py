"""
CLI entry point for the multi-site scraper.

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


def load_config(path: str) -> ScraperConfig:
    """Load scraper config from YAML file."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    config = ScraperConfig(
        name=raw["name"],
        start_urls=raw["start_urls"],
        selectors=raw["selectors"],
        pagination_selector=raw.get("pagination_selector"),
        max_pages=raw.get("max_pages", 10),
        delay_min=raw.get("delay_min", 1.0),
        delay_max=raw.get("delay_max", 3.0),
        output_format=raw.get("output_format", "csv"),
    )

    # Validate selectors format
    invalid = [k for k in config.selectors if ">" in k or "<" in k]
    if invalid:
        raise ValueError(
            f"Selector keys must be field names, not CSS. "
            f"Found: {invalid}. Got: {' '.join(config.selectors.keys())}"
        )

    return config


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
        help="Output file path (default: output/<config_name>.<format>)"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    output = args.output or f"output/{config.name}.{config.output_format}"

    async with StealthScraper(config) as scraper:
        await scraper.run()
        scraper.save(output)


if __name__ == "__main__":
    asyncio.run(main())
