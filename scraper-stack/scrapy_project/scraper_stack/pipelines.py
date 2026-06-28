# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Scrapy item pipelines: validation, dedup, CSV injection guard, export."""

import csv
import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from scrapy import Spider
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)

# Characters that trigger formula execution in Excel/LibreOffice
_CSV_DANGER_RE = re.compile(r"^[=+\-@\t\r]")


def _sanitize_csv(value: str) -> str:
    """Prefix cells starting with =, +, -, @ to prevent CSV injection."""
    if not value:
        return value
    if _CSV_DANGER_RE.match(value):
        return "'" + value
    return value


class ValidationPipeline:
    """Validate items against their Pydantic schema before further processing.

    Each item must have a ``_schema`` field (dict of field_name -> type)
    injected by the spider. Missing required fields result in DropItem.
    """

    def __init__(self):
        self.stats: dict[str, int] = {"valid": 0, "dropped": 0}

    def process_item(self, item: dict, spider: Spider) -> dict:
        schema: Optional[dict] = item.pop("_schema", None)
        if schema is None:
            # No schema defined → pass through
            self.stats["valid"] += 1
            return item

        missing = [k for k in schema if k not in item or item[k] is None]
        if missing:
            self.stats["dropped"] += 1
            logger.debug("Dropping item missing fields: %s", missing)
            raise DropItem(f"Missing required fields: {missing}")

        self.stats["valid"] += 1
        return item

    def close_spider(self, spider: Spider):
        logger.info(
            "Validation complete: %d valid, %d dropped",
            self.stats["valid"], self.stats["dropped"],
        )


class CSVInjectionGuardPipeline:
    """Sanitize all string fields to prevent CSV injection attacks."""

    def process_item(self, item: dict, spider: Spider) -> dict:
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = _sanitize_csv(value)
        return item


class DuplicateFilterPipeline:
    """Drop duplicate items based on content hash.

    Maintains an in-memory set of seen hashes. For distributed crawling,
    replace with a Redis-backed dedup (scrapy-redis).
    """

    def __init__(self):
        self._seen: set[str] = set()

    def process_item(self, item: dict, spider: Spider) -> dict:
        # Hash based on all fields except scraped_at (which varies by run)
        dedup_fields = {k: v for k, v in item.items() if k != "scraped_at"}
        item_hash = hashlib.sha256(
            json.dumps(dedup_fields, sort_keys=True, default=str).encode()
        ).hexdigest()

        if item_hash in self._seen:
            raise DropItem(f"Duplicate item (hash={item_hash[:12]}...)")
        self._seen.add(item_hash)
        return item


class MultiFormatExportPipeline:
    """Export items to the configured output format(s).

    Configuration via spider attributes or command-line:
        spider.output_dir = "output/"
        spider.output_formats = ["csv", "json"]
    """

    def __init__(self):
        self._items: list[dict] = []

    def process_item(self, item: dict, spider: Spider) -> dict:
        item.setdefault("scraped_at", datetime.now(timezone.utc).isoformat())
        self._items.append(dict(item))
        return item

    def close_spider(self, spider: Spider):
        if not self._items:
            logger.warning("No items to export")
            return

        output_dir = Path(getattr(spider, "output_dir", "output"))
        output_dir.mkdir(parents=True, exist_ok=True)
        formats = getattr(spider, "output_formats", ["csv", "json"])
        spider_name = spider.name

        for fmt in formats:
            path = output_dir / f"{spider_name}.{fmt}"
            try:
                if fmt == "csv":
                    _write_csv(path, self._items)
                elif fmt == "json":
                    path.write_text(
                        json.dumps(self._items, indent=2, ensure_ascii=False, default=str),
                        encoding="utf-8",
                    )
                elif fmt == "xlsx":
                    _write_xlsx(path, self._items)
                logger.info("Exported %d items → %s", len(self._items), path)
            except Exception as exc:
                logger.error("Failed to export %s: %s", fmt, exc)


def _write_csv(path: Path, items: list[dict]) -> None:
    if not items:
        return
    fieldnames = list(items[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow({k: _sanitize_csv(str(v)) for k, v in item.items()})


def _write_xlsx(path: Path, items: list[dict]) -> None:
    try:
        from openpyxl import Workbook
    except ImportError:
        logger.error("openpyxl not installed — skipping XLSX export")
        return
    wb = Workbook()
    ws = wb.active
    if items:
        ws.append(list(items[0].keys()))
        for item in items:
            ws.append([str(v) for v in item.values()])
    wb.save(path)
