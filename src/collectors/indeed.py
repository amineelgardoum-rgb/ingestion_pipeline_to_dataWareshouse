import pandas as pd
import time
import random
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from jobspy import scrape_jobs
from config import settings
from src.utils.helpers import setup_logging

logger = setup_logging("collector.indeed")

MAX_WORKERS     = 5      # keep low — Indeed blocks fast
MAX_RETRIES     = 3
BASE_BACKOFF    = 2
MAX_BACKOFF     = 30
TERM_DELAY      = (1, 3)  # indeed is more aggressive than emploi.ma
RESULTS_WANTED  = 50
HOURS_OLD       = 168
FALLBACK_HOURS  = 720


# ─────────────────────────────────────────
# PER TASK SCRAPER
# ─────────────────────────────────────────
def _scrape_task(
    term: str,
    location: str,
    seen_urls: set,
    lock: Lock,
    results_wanted: int = RESULTS_WANTED,
    hours_old: int = HOURS_OLD,
) -> list[dict]:
    time.sleep(random.uniform(*TERM_DELAY))
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"[{attempt}/{MAX_RETRIES}] '{term}' @ '{location}'")
            jobs = scrape_jobs(
                site_name=["indeed"],
                search_term=term,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                country_indeed="Morocco",
            )

            if jobs is not None and not jobs.empty:
                # deduplicate against global seen set
                new_rows = []
                with lock:
                    for _, row in jobs.iterrows():
                        url = row.get("job_url", "")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            new_rows.append(row)

                logger.info(f"  ✓ {len(new_rows)} new jobs — '{term}' @ '{location}'")
                return new_rows

            # no results → fallback to wider window
            logger.info(f"  → No results, trying {FALLBACK_HOURS}h window...")
            jobs = scrape_jobs(
                site_name=["indeed"],
                search_term=term,
                location=location,
                results_wanted=results_wanted,
                hours_old=FALLBACK_HOURS,
                country_indeed="Morocco",
            )

            if jobs is not None and not jobs.empty:
                new_rows = []
                with lock:
                    for _, row in jobs.iterrows():
                        url = row.get("job_url", "")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            new_rows.append(row)
                logger.info(f"  ✓ {len(new_rows)} new jobs (fallback) — '{term}' @ '{location}'")
                return new_rows

            logger.info(f"  ✗ No jobs found — '{term}' @ '{location}'")
            return []

        except Exception as e:
            last_error   = e
            err_str      = str(e).lower()
            backoff      = min(BASE_BACKOFF ** attempt + random.uniform(1, 3), MAX_BACKOFF)

            if any(x in err_str for x in ["429", "rate limit", "too many"]):
                backoff = MAX_BACKOFF
                logger.warning(f"  ⚠ Rate limited! Waiting {backoff:.0f}s...")
            elif any(x in err_str for x in ["blocked", "captcha", "403"]):
                logger.warning(f"  ⚠ Blocked on attempt {attempt}")
            else:
                logger.warning(f"  ⚠ Attempt {attempt} failed: {e}")

            if attempt < MAX_RETRIES:
                logger.info(f"  → Retrying in {backoff:.1f}s...")
                time.sleep(backoff)

    logger.error(f"  ✗ All {MAX_RETRIES} attempts failed — '{term}' @ '{location}': {last_error}")
    return []


# ─────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────
def collect(
    results_wanted: int = RESULTS_WANTED,
    hours_old: int = HOURS_OLD,
    max_workers: int = MAX_WORKERS,
) -> pd.DataFrame:
    tasks = [
        (term, loc)
        for term in settings.SEARCH_TERMS
        for loc  in settings.LOCATIONS
    ]

    logger.info("=" * 50)
    logger.info(f"Starting Indeed — {len(settings.SEARCH_TERMS)} terms × {len(settings.LOCATIONS)} locations = {len(tasks)} tasks")
    logger.info(f"Workers: {max_workers}")
    logger.info("=" * 50)

    seen_urls = set()
    lock      = Lock()
    all_rows  = []
    start     = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_scrape_task, term, loc, seen_urls, lock, results_wanted, hours_old): (term, loc)
            for term, loc in tasks
        }
        for future in as_completed(futures):
            term, loc = futures[future]
            try:
                rows = future.result()
                all_rows.extend(rows)
            except Exception as e:
                logger.error(f"  ✗ Thread crashed '{term}' @ '{loc}': {e}")

    logger.info(f"Done in {time.time() - start:.1f}s — {len(all_rows)} unique jobs")

    if not all_rows:
        logger.warning("No Indeed jobs collected.")
        return pd.DataFrame()

    return pd.DataFrame(all_rows).reset_index(drop=True)


if __name__ == "__main__":
    df = collect()
    if not df.empty:
        print(f"\nShape: {df.shape}")
        print(df[["title", "company", "location"]].head(10))
    else:
        print("No data collected.")