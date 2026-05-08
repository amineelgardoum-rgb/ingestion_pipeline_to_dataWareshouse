import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from urllib.parse import urlencode

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config import settings
from src.utils.helpers import setup_logging

logger = setup_logging("collector.rekrute")

BASE_URL   = "https://www.rekrute.com"
SEARCH_URL = "https://www.rekrute.com/offres.html"
HEADERS    = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

MAX_WORKERS = 5
MAX_PAGES   = 10
PAGE_DELAY  = (0.5, 1.5)
TERM_DELAY  = (0.3, 0.8)


# ─────────────────────────────────────────
# PAGE PARSER
# ─────────────────────────────────────────
def _parse_page(html: str, term: str, seen_urls: set, lock: Lock) -> list[dict]:
    soup     = BeautifulSoup(html, "html.parser")
    cards    = soup.select(".post-id")
    new_jobs = []

    for card in cards:
        try:
            title_tag    = card.select_one("a.titreJob") or card.select_one("h2 a")
            company_tag  = card.select_one(".recruteur")  or card.select_one(".company")
            location_tag = card.select_one(".location")
            date_tag     = card.select_one(".date")

            if not title_tag:
                continue

            href    = title_tag.get("href", "")
            job_url = BASE_URL + href if href.startswith("/") else href

            if not job_url:
                continue

            with lock:
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

            new_jobs.append({
                "source":      "rekrute",
                "title":       title_tag.get_text(strip=True)    if title_tag    else "",
                "company":     company_tag.get_text(strip=True)  if company_tag  else "",
                "location":    location_tag.get_text(strip=True) if location_tag else "",
                "date_posted": date_tag.get_text(strip=True)     if date_tag     else "",
                "job_url":     job_url,
                "search_term": term,
            })

        except Exception as e:
            logger.error(f"  → Card parse error: {e}")

    return new_jobs


# ─────────────────────────────────────────
# PER-TERM SCRAPER
# ─────────────────────────────────────────
def _scrape_term(term: str, seen_urls: set, lock: Lock, max_pages: int = MAX_PAGES) -> list[dict]:
    time.sleep(random.uniform(*TERM_DELAY))

    jobs    = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for page in range(1, max_pages + 1):
        params = {"p": page, "s": 1, "q": term}
        try:
            res = session.get(SEARCH_URL, params=params, timeout=15)
            res.raise_for_status()

            new_jobs = _parse_page(res.text, term, seen_urls, lock)

            if not new_jobs:
                logger.info(f"  → '{term}' page {page}: no new jobs, stopping")
                break

            jobs.extend(new_jobs)
            logger.info(f"  → '{term}' page {page}: +{len(new_jobs)} jobs ({len(jobs)} total)")
            time.sleep(random.uniform(*PAGE_DELAY))

        except requests.HTTPError as e:
            logger.error(f"  → HTTP error for '{term}' page {page}: {e}")
            break
        except Exception as e:
            logger.error(f"  → Error for '{term}' page {page}: {e}")
            break

    return jobs


# ─────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────
def collect(max_pages: int = MAX_PAGES, max_workers: int = MAX_WORKERS) -> pd.DataFrame:
    logger.info("=" * 50)
    logger.info(f"Starting Rekrute — {len(settings.SEARCH_TERMS)} terms, {max_workers} workers")
    logger.info("=" * 50)

    seen_urls = set()
    lock      = Lock()
    all_jobs  = []
    start     = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_scrape_term, term, seen_urls, lock, max_pages): term
            for term in settings.SEARCH_TERMS
        }
        for future in as_completed(futures):
            term = futures[future]
            try:
                results = future.result()
                all_jobs.extend(results)
                logger.info(f"  ✓ '{term}' done — {len(results)} jobs")
            except Exception as e:
                logger.error(f"  ✗ '{term}' crashed: {e}")

    logger.info(f"Done in {time.time() - start:.1f}s — {len(all_jobs)} total jobs")

    if not all_jobs:
        logger.warning("No Rekrute jobs found.")
        return pd.DataFrame()

    df     = pd.DataFrame(all_jobs)
    before = len(df)
    df     = df.drop_duplicates(subset=["job_url"])
    logger.info(f"Deduped: {before} → {len(df)} unique jobs")
    return df


if __name__ == "__main__":
    df = collect()
    if not df.empty:
        print(f"\nShape: {df.shape}")
        print(df[["title", "company", "location", "date_posted"]].head(10))
    else:
        print("No data collected.")