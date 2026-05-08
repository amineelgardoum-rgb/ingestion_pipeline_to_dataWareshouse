import pandas as pd
from jobspy import scrape_jobs
from config import settings
from src.utils.helpers import setup_logging

logger = setup_logging("collector.indeed")

def collect(results_wanted=50, hours_old=168):
    """Scrape job listings from Indeed for configured terms and locations."""
    all_jobs = []
    
    logger.info("Starting Indeed collection...")
    for term in settings.SEARCH_TERMS:
        for location in settings.LOCATIONS:
            try:
                logger.info(f"Scraping: '{term}' in '{location}'...")
                jobs = scrape_jobs(
                    site_name=["indeed"],
                    search_term=term,
                    location=location,
                    results_wanted=results_wanted,
                    hours_old=hours_old,
                    country_indeed='Morocco',
                )
                if not jobs.empty:
                    all_jobs.append(jobs)
                    logger.info(f"  → {len(jobs)} jobs found")
                else:
                    logger.info("  → No jobs found")

            except Exception as e:
                logger.error(f"  → Failed: {e}")

    if not all_jobs:
        logger.warning("No Indeed jobs found.")
        return pd.DataFrame()

    combined = pd.concat(all_jobs, ignore_index=True)
    before = len(combined)
    combined = combined.drop_duplicates(subset=["job_url"])
    after = len(combined)
    logger.info(f"Deduplication: {before} → {after} unique jobs")
    
    return combined
