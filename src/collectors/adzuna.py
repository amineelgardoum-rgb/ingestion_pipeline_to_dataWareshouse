import requests
import pandas as pd
from config import settings
from src.utils.helpers import setup_logging

logger = setup_logging("collector.adzuna")

def collect():
    """Scrape job listings from Adzuna API."""
    all_jobs = []
    logger.info("Starting Adzuna collection...")
    
    # Adzuna typically works better with broader queries for countries
    country_code = "ma" # Morocco
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    
    for term in settings.SEARCH_TERMS:
        for location in settings.LOCATIONS:
            params = {
                "app_id": settings.ADZUNA_APP_ID,
                "app_key": settings.ADZUNA_APP_KEY,
                "results_per_page": 50,
                "what": term,
                "where": location,
                "content-type": "application/json",
            }

            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                results = response.json().get("results", [])
                
                if results:
                    batch = pd.DataFrame([{
                        "title":       r.get("title"),
                        "company":     r.get("company", {}).get("display_name"),
                        "location":    r.get("location", {}).get("display_name"),
                        "description": r.get("description"),
                        "job_url":     r.get("redirect_url"),
                        "salary_min":  r.get("salary_min"),
                        "salary_max":  r.get("salary_max"),
                        "date_posted": r.get("created"),
                        "source":      "adzuna",
                        "search_term": term
                    } for r in results])
                    all_jobs.append(batch)
                    logger.info(f"  → Found {len(batch)} jobs for '{term}' in '{location}'")
            except Exception as e:
                logger.error(f"  → Adzuna error for '{term}': {e}")

    if not all_jobs:
        return pd.DataFrame()
        
    df = pd.concat(all_jobs, ignore_index=True)
    df = df.drop_duplicates(subset=["job_url"])
    return df
