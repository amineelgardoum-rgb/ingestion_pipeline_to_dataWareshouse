import pandas as pd
import sys
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from jobspy import scrape_jobs
from config import settings
from src.utils.helpers import setup_logging

logger = setup_logging("collector.linkedin")

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
MAX_WORKERS       = 5
MAX_RETRIES       = 4
BASE_BACKOFF      = 2
MAX_BACKOFF       = 30
RATE_LIMIT_DELAY  = (2, 5)
RESULTS_PER_QUERY = 50
HOURS_OLD         = 168
FALLBACK_HOURS    = 720


# ─────────────────────────────────────────
# STATS
# ─────────────────────────────────────────
def make_stats():
    return {"success": 0, "failed": 0, "empty": 0, "total_jobs": 0, "_lock": Lock()}

def update_stat(stats: dict, key: str, value: int = 1):
    with stats["_lock"]:
        stats[key] += value

def report_stats(stats: dict):
    logger.info(f"  ✓ Successful : {stats['success']}")
    logger.info(f"  ✗ Failed     : {stats['failed']}")
    logger.info(f"  ~ Empty      : {stats['empty']}")
    logger.info(f"  📦 Total jobs : {stats['total_jobs']}")


# ─────────────────────────────────────────
# SCRAPER
# ─────────────────────────────────────────
def _call_api(term: str, location: str, hours_old: int, results_wanted: int) -> pd.DataFrame:
    time.sleep(random.uniform(*RATE_LIMIT_DELAY))
    return scrape_jobs(
        site_name=["linkedin"],
        search_term=term,
        location=location,
        results_wanted=results_wanted,
        hours_old=hours_old,
        linkedin_fetch_description=False,
    )


def _scrape_single(
    term: str,
    location: str,
    stats: dict,
    max_retries: int = MAX_RETRIES,
    results_wanted: int = RESULTS_PER_QUERY,
    hours_old: int = HOURS_OLD,
) -> pd.DataFrame:
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[{attempt}/{max_retries}] '{term}' @ '{location}'")
            jobs = _call_api(term, location, hours_old, results_wanted)

            if jobs is not None and not jobs.empty:
                update_stat(stats, "success")
                update_stat(stats, "total_jobs", len(jobs))
                logger.info(f"  ✓ {len(jobs)} jobs — '{term}' @ '{location}'")
                return jobs

            logger.info(f"  → No results, trying {FALLBACK_HOURS}h window...")
            jobs = _call_api(term, location, FALLBACK_HOURS, results_wanted)

            if jobs is not None and not jobs.empty:
                update_stat(stats, "success")
                update_stat(stats, "total_jobs", len(jobs))
                logger.info(f"  ✓ {len(jobs)} jobs (fallback) — '{term}' @ '{location}'")
                return jobs

            update_stat(stats, "empty")
            logger.info(f"  ✗ No jobs found — '{term}' @ '{location}'")
            return pd.DataFrame()

        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            backoff = min(BASE_BACKOFF ** attempt + random.uniform(1, 3), MAX_BACKOFF)

            if any(x in err_str for x in ["429", "rate limit", "too many requests"]):
                backoff = MAX_BACKOFF
                logger.warning(f"  ⚠ Rate limited! Waiting {backoff:.0f}s...")
            elif any(x in err_str for x in ["blocked", "captcha", "403"]):
                logger.warning(f"  ⚠ Blocked/CAPTCHA on attempt {attempt}")
            else:
                logger.warning(f"  ⚠ Attempt {attempt} failed: {e}")

            if attempt < max_retries:
                logger.info(f"  → Retrying in {backoff:.1f}s...")
                time.sleep(backoff)

    update_stat(stats, "failed")
    logger.error(f"  ✗ All {max_retries} attempts failed — '{term}' @ '{location}': {last_error}")
    return pd.DataFrame()


# ─────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────
def collect(
    results_wanted: int = RESULTS_PER_QUERY,
    hours_old: int = HOURS_OLD,
    max_workers: int = MAX_WORKERS,
) -> pd.DataFrame:
    stats = make_stats()
    tasks = [(term, loc) for term in settings.SEARCH_TERMS for loc in settings.LOCATIONS]

    logger.info("=" * 50)
    logger.info(f"Starting LinkedIn collection...")
    logger.info(f"Terms: {len(settings.SEARCH_TERMS)} | Locations: {len(settings.LOCATIONS)} | Workers: {max_workers}")
    logger.info(f"Total tasks: {len(tasks)}")
    logger.info("=" * 50)

    start = time.time()
    all_jobs = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_scrape_single, term, loc, stats, MAX_RETRIES, results_wanted, hours_old): (term, loc)
            for term, loc in tasks
        }
        for future in as_completed(futures):
            term, loc = futures[future]
            try:
                result = future.result(timeout=120)
                if result is not None and not result.empty:
                    all_jobs.append(result)
            except Exception as e:
                logger.error(f"  ✗ Thread crashed for '{term}' @ '{loc}': {e}")
                update_stat(stats, "failed")

    logger.info("=" * 50)
    logger.info(f"Done in {time.time() - start:.1f}s")
    report_stats(stats)
    logger.info("=" * 50)

    if not all_jobs:
        logger.warning("No jobs collected.")
        return pd.DataFrame()

    combined = pd.concat(all_jobs, ignore_index=True)
    before = len(combined)
    combined = combined.drop_duplicates(subset=["job_url"])
    logger.info(f"Deduped: {before} → {len(combined)} unique jobs")

    return combined


if __name__ == "__main__":
    df = collect(results_wanted=20, hours_old=168)
    if not df.empty:
        print(f"\nShape: {df.shape}")
        print(df[["title", "company", "location"]].head(10))
    else:
        print("No data collected.")