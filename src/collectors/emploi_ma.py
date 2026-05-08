import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from config import settings
from src.utils.helpers import setup_logging

logger = setup_logging("collector.emploi_ma")

BASE_URL = "https://www.emploi.ma"
SEARCH_URL = "https://www.emploi.ma/recherche-jobs-maroc/{term}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

def scrape_emploi_ma_term(term, max_pages=5):
    """Scrape listings from Emploi.ma for a term."""
    jobs = []
    url = SEARCH_URL.format(term=term.replace(" ", "%20"))
    seen_urls = set()

    for page in range(1, max_pages + 1):
        page_url = url if page == 1 else f"{url}?p={page}"
        try:
            res = requests.get(page_url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(res.text, "html.parser")
            job_cards = soup.select(".card-job")
            if not job_cards: break

            for card in job_cards:
                try:
                    title_tag = card.select_one("h2 a") or card.select_one("a")
                    href = title_tag.get("href", "") if title_tag else ""
                    job_url = BASE_URL + href if href.startswith("/") else href
                    
                    if job_url in seen_urls: continue
                    seen_urls.add(job_url)

                    company_tag = card.select_one(".card-job-company") or card.select_one(".company-name")
                    location_tag = card.select_one(".card-job-description") or card.select_one(".job-description")

                    jobs.append({
                        "source": "emploi_ma",
                        "title": title_tag.get_text(strip=True) if title_tag else "",
                        "company": company_tag.get_text(strip=True) if company_tag else "",
                        "location": location_tag.get_text(strip=True) if location_tag else "",
                        "job_url": job_url,
                        "search_term": term,
                    })
                except: continue
            time.sleep(1)
        except: break
    return jobs

def collect(max_pages=5):
    """Scrape job listings from Emploi.ma."""
    all_jobs = []
    logger.info("Starting Emploi.ma collection...")
    for term in settings.SEARCH_TERMS:
        logger.info(f"Scraping: '{term}'...")
        results = scrape_emploi_ma_term(term, max_pages=max_pages)
        all_jobs.extend(results)
        
    if not all_jobs:
        return pd.DataFrame()
        
    df = pd.DataFrame(all_jobs)
    df = df.drop_duplicates(subset=["job_url"])
    return df
