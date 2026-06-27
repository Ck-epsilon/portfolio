# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Playwright-based web scraper engine.

Drives a headless Chromium browser to navigate pages, extract structured
data via CSS selectors, handle pagination, and emit real-time log messages.
"""

import asyncio
from typing import Any

from playwright.async_api import TimeoutError as PwTimeoutError
from playwright.async_api import async_playwright, Page

from task_queue import TaskStatus


DEFAULT_CONFIG = {
    "selector": "body",
    "fields": [],
    "max_pages": 1,
    "wait_selector": "",
    "delay_ms": 1000,
    "screenshot": False,
}


async def scrape_task(task) -> None:
    """Execute a full scrape task.

    Updates *task* in-place: pushes log messages to ``task.log_queue``,
    sets ``task.results`` / ``task.error``.
    """
    config = {**DEFAULT_CONFIG, **task.config}
    url = task.url

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await task.log_queue.put({
                "type": "log", "level": "info",
                "message": f"Navigating to {url}"
            })
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            if config.get("wait_selector"):
                await page.wait_for_selector(config["wait_selector"], timeout=10000)
                await task.log_queue.put({
                    "type": "log", "level": "info",
                    "message": f"Selector '{config['wait_selector']}' appeared"
                })

            # Initial delay for dynamic content
            await asyncio.sleep(config.get("delay_ms", 1000) / 1000)

            total = 0
            for page_num in range(1, config.get("max_pages", 1) + 1):
                task.current_page = page_num

                await task.log_queue.put({
                    "type": "progress",
                    "page": page_num,
                    "total_pages": config.get("max_pages", 1),
                    "message": f"Scraping page {page_num}/{config['max_pages']}"
                })

                rows = await _extract_page(page, config, task.log_queue)
                task.results.extend(rows)
                total += len(rows)
                task.rows_scraped = total
                task.pages_scraped = page_num

                await task.log_queue.put({
                    "type": "log", "level": "info",
                    "message": f"Page {page_num}: {len(rows)} rows extracted ({total} total)"
                })

                # Pagination: try to click next or stop
                if page_num < config.get("max_pages", 1):
                    if not await _goto_next_page(page, config, task.log_queue):
                        await task.log_queue.put({
                            "type": "log", "level": "warn",
                            "message": "No next page found, stopping pagination early"
                        })
                        break

            await task.log_queue.put({
                "type": "complete",
                "total_rows": total,
                "total_pages": task.pages_scraped,
                "message": f"Scrape complete: {total} rows across {task.pages_scraped} pages"
            })
            task.status = TaskStatus.COMPLETED

        except Exception as exc:
            task.error = str(exc)
            await task.log_queue.put({
                "type": "error", "message": f"Scrape failed: {exc}"
            })
            task.status = TaskStatus.FAILED
        finally:
            await browser.close()


async def _extract_page(
    page: Page, config: dict, log_queue: asyncio.Queue
) -> list[dict[str, Any]]:
    """Extract structured data from the current page.

    Logs warnings to *log_queue* when selectors are not found, but
    returns partial results rather than failing outright.
    """
    selector = config.get("selector", "body")
    fields = config.get("fields", [])

    # Wait for selector to appear
    try:
        await page.wait_for_selector(selector, timeout=5000)
    except PwTimeoutError:
        await log_queue.put({
            "type": "log", "level": "warn",
            "message": f"Selector '{selector}' not found within 5s — no data extracted"
        })
        return []
    except Exception as exc:
        await log_queue.put({
            "type": "error",
            "message": f"Selector wait error for '{selector}': {exc}"
        })
        return []

    # If no fields specified, extract text content
    if not fields:
        elements = await page.query_selector_all(selector)
        rows = []
        for el in elements:
            text = await el.inner_text()
            if text.strip():
                rows.append({"text": text.strip()})
        return rows

    # Structured extraction with named fields
    rows = []
    elements = await page.query_selector_all(selector)
    for el in elements:
        row = {}
        for field in fields:
            name = field.get("name", "value")
            sub_selector = field.get("selector", "&")
            try:
                sub_el = (
                    await el.query_selector(sub_selector)
                    if sub_selector != "&"
                    else el
                )
                if sub_el:
                    value = await _extract_field_value(sub_el, field)
                    row[name] = value
            except PwTimeoutError:
                row[name] = ""
                await log_queue.put({
                    "type": "log", "level": "warn",
                    "message": f"Field '{name}' selector '{sub_selector}' not found"
                })
            except Exception as exc:
                row[name] = ""
                await log_queue.put({
                    "type": "error",
                    "message": f"Field '{name}' extraction error: {exc}"
                })
        if any(v for v in row.values()):
            rows.append(row)
    return rows


async def _extract_field_value(element, field: dict) -> str:
    """Extract a value from a Playwright element based on field config."""
    extract_type = field.get("type", "text")
    attr = field.get("attr", "")

    if extract_type == "text":
        return (await element.inner_text()).strip()
    elif extract_type == "html":
        return await element.inner_html()
    elif extract_type == "attribute" and attr:
        return (await element.get_attribute(attr)) or ""
    return (await element.inner_text()).strip()


async def _goto_next_page(
    page: Page, config: dict, log_queue: asyncio.Queue
) -> bool:
    """Attempt to navigate to the next page. Returns True on success."""
    next_selector = config.get("next_selector", "")
    if not next_selector:
        return False

    try:
        next_btn = await page.query_selector(next_selector)
        if next_btn:
            await next_btn.click()
            await asyncio.sleep(config.get("delay_ms", 1000) / 1000)
            await log_queue.put({
                "type": "log", "level": "info",
                "message": f"Clicked next page via '{next_selector}'"
            })
            return True
    except PwTimeoutError:
        await log_queue.put({
            "type": "log", "level": "warn",
            "message": f"Next page selector '{next_selector}' not found"
        })
    except Exception as exc:
        await log_queue.put({
            "type": "error",
            "message": f"Next page click error: {exc}"
        })

    # Try URL-based pagination pattern
    pagination_pattern = config.get("pagination_url", "")
    if pagination_pattern:
        try:
            next_url = pagination_pattern.replace(
                "{page}", str(config.get("_next_page_num", 2))
            )
            await page.goto(next_url, wait_until="domcontentloaded")
            config["_next_page_num"] = config.get("_next_page_num", 2) + 1
            return True
        except PwTimeoutError:
            await log_queue.put({
                "type": "log", "level": "warn",
                "message": f"Pagination URL '{next_url}' timed out"
            })
        except Exception as exc:
            await log_queue.put({
                "type": "error",
                "message": f"Pagination URL error: {exc}"
            })

    return False
