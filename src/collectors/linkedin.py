import pandas as pd
from jobspy import scrape_jobs
from config import settings
from src.utils.helpers import setup_logging

logger = setup_logging("collector.linkedin")

def collect(results_wanted=50, hours_old=168):
    """Scrape job listings from LinkedIn for configured terms and locations."""
    all_jobs = []
    
    logger.info("Starting LinkedIn collection...")
    for term in settings.SEARCH_TERMS:
        for location in settings.LOCATIONS:
            try:
                logger.info(f"Scraping: '{term}' in '{location}'...")
                jobs = scrape_jobs(
                    site_name=["linkedin"],
                    search_term=term,
                    location=location,
                    results_wanted=results_wanted,
                    hours_old=hours_old,
                )
                if not jobs.empty:
                    all_jobs.append(jobs)
                    logger.info(f"  → {len(jobs)} jobs found")
                else:
                    logger.info("  → No jobs found")

            except Exception as e:
                logger.error(f"  → Failed: {e}")

    if not all_jobs:
        return pd.DataFrame()

    combined = pd.concat(all_jobs, ignore_index=True)
    combined = combined.drop_duplicates(subset=["job_url"])
    return combined
