# Author: Ck.epsilon
"""End-to-end pipeline: scrape → clean → store. Premium tier feature.

Reads YAML config including optional pipeline stages.

Usage:
    python pipeline.py --config sites/example.yaml
    python pipeline.py --config sites/example.yaml --output data.db
"""

import argparse
import asyncio
from pathlib import Path

import yaml

from scraper.engine import ScraperConfig, StealthScraper


async def run_pipeline(config_path: str, output_path: str | None = None):
    """Run the full pipeline: scrape → clean → store."""
    raw = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    config = ScraperConfig(
        name=raw["name"],
        start_urls=raw["start_urls"],
        selectors=raw["selectors"],
        pagination_selector=raw.get("pagination_selector"),
        max_pages=raw.get("max_pages", 10),
        delay_min=raw.get("delay_min", 1.0),
        delay_max=raw.get("delay_max", 3.0),
        max_retries=raw.get("max_retries", 3),
        retry_backoff=raw.get("retry_backoff", 2.0),
        output_format=raw.get("output_format", "csv"),
        login_url=raw.get("login_url"),
        login_selector=raw.get("login_selector"),
        login_credentials=raw.get("login_credentials"),
    )

    async with StealthScraper(config) as scraper:
        # Stage 1: Scrape
        await scraper.run()
        raw_count = len(scraper.results)
        print(f"[PIPELINE] Stage 1 ✓ Scraped {raw_count} items")

        # Stage 2: Clean (when cleaning config present)
        cleaning = raw.get("cleaning", {})
        if cleaning:
            scraper.clean_data(
                dedup_keys=cleaning.get("dedup_keys"),
                normalize_fields=cleaning.get("normalize_fields"),
                required_fields=cleaning.get("required_fields"),
            )
            print(f"[PIPELINE] Stage 2 ✓ Cleaned → {len(scraper.results)} items (dropped {raw_count - len(scraper.results)})")

        # Stage 3: Store (auto-detect format)
        store = raw.get("store", {})
        store_path = output_path or store.get("path", "output/pipeline_results")

        if store.get("db"):
            scraper.save_db(store.get("db"), store.get("table", "results"))
            print(f"[PIPELINE] Stage 3 ✓ Stored to SQLite")
        elif store.get("format") == "excel" or (store_path and store_path.endswith(".xlsx")):
            scraper.save_excel(store_path)
            print(f"[PIPELINE] Stage 3 ✓ Stored to Excel: {store_path}")
        else:
            fmt = store.get("format", "csv")
            if not store_path.endswith(f".{fmt}"):
                store_path = f"{store_path}.{fmt}"
            scraper.save(store_path)
            print(f"[PIPELINE] Stage 3 ✓ Stored to {fmt}: {store_path}")

        # Stage 4: Alert (when thresholds breached)
        alerts = raw.get("alerts", {})
        if alerts:
            min_expected = alerts.get("min_expected")
            if min_expected and len(scraper.results) < min_expected:
                print(f"[PIPELINE] ⚠ ALERT: Only {len(scraper.results)} items (expected ≥{min_expected})")
                if alerts.get("email_to"):
                    _send_alert(
                        alerts["email_to"],
                        f"[{config.name}] Low yield: {len(scraper.results)} items",
                        alerts.get("smtp_host", "smtp.qq.com"),
                        alerts.get("smtp_port", 587),
                        alerts.get("smtp_user", ""),
                        alerts.get("smtp_password", ""),
                    )


def _send_alert(to: str, subject: str, smtp_host: str, smtp_port: int,
                smtp_user: str, smtp_password: str):
    """Send email alert via SMTP (best-effort, logs on failure)."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(subject)
        msg["Subject"] = subject
        msg["From"] = smtp_user or "scraper@localhost"
        msg["To"] = to
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as s:
            s.starttls()
            if smtp_user:
                s.login(smtp_user, smtp_password)
            s.send_message(msg)
        print(f"[PIPELINE] Alert email sent to {to}")
    except Exception as e:
        logger.warning("Failed to send alert email: %s", e)


async def main():
    parser = argparse.ArgumentParser(description="Scraper Pipeline — Premium tier")
    parser.add_argument("--config", "-c", required=True, help="YAML config with pipeline stages")
    parser.add_argument("--output", "-o", help="Output path override")
    args = parser.parse_args()
    await run_pipeline(args.config, args.output)


if __name__ == "__main__":
    asyncio.run(main())
