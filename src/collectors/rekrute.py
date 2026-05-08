import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from config import settings
from src.utils.helpers import setup_logging

logger = setup_logging("collector.rekrute")

BASE_URL = "https://www.rekrute.com"
SEARCH_URL = "https://www.rekrute.com/offres.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

def scrape_rekrute_term(search_term, max_pages=10):
    """Scrape listings for a specific term."""
    jobs = []
    page = 1
    while page <= max_pages:
        params = {"p": page, "s": 1, "q": search_term}
        try:
            res = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(res.text, "html.parser")
            job_cards = soup.select(".post-id")
            if not job_cards: 
                break

            for card in job_cards:
                try:
                    title_tag = card.select_one("a.titreJob") or card.select_one("h2 a")
                    company_tag = card.select_one(".recruteur") or card.select_one(".company")
                    location_tag = card.select_one(".location")
                    date_tag = card.select_one(".date")
                    
                    jobs.append({
                        "source": "rekrute",
                        "title": title_tag.get_text(strip=True) if title_tag else "",
                        "company": company_tag.get_text(strip=True) if company_tag else "",
                        "location": location_tag.get_text(strip=True) if location_tag else "",
                        "date_posted": date_tag.get_text(strip=True) if date_tag else "",
                        "job_url": BASE_URL + title_tag["href"] if title_tag else "",
                        "search_term": search_term,
                    })
                except: continue
            page += 1
            time.sleep(1)
        except: break
    return jobs

def collect(max_pages=10):
    """Scrape job listings from Rekrute."""
    all_jobs = []
    logger.info("Starting Rekrute collection...")
    for term in settings.SEARCH_TERMS:
        logger.info(f"Scraping: '{term}'...")
        results = scrape_rekrute_term(term, max_pages=max_pages)
        all_jobs.extend(results)
    
    if not all_jobs:
        logger.warning("No Rekrute jobs found.")
        return pd.DataFrame()
        
    df = pd.DataFrame(all_jobs)
    before = len(df)
    df = df.drop_duplicates(subset=["job_url"])
    after = len(df)
    logger.info(f"Deduplication: {before} → {after} unique jobs")
    return df
