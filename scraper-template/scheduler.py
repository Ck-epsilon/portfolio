# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Cron scheduler for periodic scraper runs. Premium tier feature.

Usage:
    python scheduler.py --config sites/hackernews.yaml --every 3600
    python scheduler.py --config sites/example.yaml --at "09:00" --output data.csv
"""

import argparse
import asyncio
import time
from datetime import datetime, timedelta


def _parse_interval(interval_str: str) -> float:
    """Parse interval string with units: 3600, 1h, 30m, 2h30m."""
    interval_str = interval_str.strip().lower()
    if interval_str.isdigit():
        return float(interval_str)
    total = 0.0
    unit_map = {"h": 3600, "m": 60, "s": 1}
    for unit, seconds in unit_map.items():
        if unit in interval_str:
            num_str = interval_str.split(unit)[0]
            parts = num_str.split()[-1].split(",")[-1]
            try:
                total += float(parts) * seconds
            except ValueError:
                pass
    return total if total > 0 else 3600.0


async def run_scraper_proc(config_path: str, output_path: str | None) -> bool:
    """Run scraper via subprocess to isolate each run."""
    import subprocess
    import sys
    cmd = [sys.executable, "run.py", "--config", config_path]
    if output_path:
        cmd.extend(["--output", output_path])
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        print(f"[SCHEDULER] Failed: {stderr.decode()}")
        return False
    print(f"[SCHEDULER] OK: {stdout.decode().strip().split(chr(10))[-1]}")
    return True


async def main():
    parser = argparse.ArgumentParser(description="Scraper Scheduler — Premium tier")
    parser.add_argument("--config", "-c", required=True, help="Path to YAML config")
    parser.add_argument("--output", "-o", help="Output path override")
    parser.add_argument("--every", help="Interval between runs (e.g., 3600, 1h, 30m)")
    parser.add_argument("--at", help="Run at specific time daily (HH:MM)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    if args.once:
        await run_scraper_proc(args.config, args.output)
        return

    if args.at:
        # Parse daily time
        h, m = map(int, args.at.split(":"))
        interval = 86400  # check every 60s until target time
    elif args.every:
        interval = _parse_interval(args.every)
    else:
        interval = 3600.0

    print(f"[SCHEDULER] Starting. Config={args.config}, interval={interval}s")
    if args.at:
        print(f"[SCHEDULER] Will run daily at {args.at}")

    while True:
        now = datetime.now()
        if args.at:
            target = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if now > target:
                target += timedelta(days=1)
            wait = (target - now).total_seconds()
            print(f"[SCHEDULER] Next run at {target.strftime('%H:%M')} (wait {wait:.0f}s)")
            await asyncio.sleep(min(wait, 60))
            if wait > 60:
                continue

        await run_scraper_proc(args.config, args.output)

        if args.once:
            break
        await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())
