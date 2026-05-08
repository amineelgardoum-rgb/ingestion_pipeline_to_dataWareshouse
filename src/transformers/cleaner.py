import pandas as pd
from src.utils.helpers import clean_text, setup_logging

logger = setup_logging("transformer.cleaner")

def clean_data(df):
    """Applies standardized cleaning to the job listings dataframe."""
    if df.empty:
        return df
        
    logger.info(f"Cleaning {len(df)} rows...")
    
    # Apply text sanitization to all string columns
    df = df.apply(lambda col: col.map(clean_text) if col.dtype == "object" else col)
    
    # Ensure mandatory columns exist
    mandatory_cols = ["source", "title", "company", "location", "job_url", "search_term"]
    for col in mandatory_cols:
        if col not in df.columns:
            df[col] = ""
            
    # Remove duplicates one last time across all sources if applicable
    before = len(df)
    df = df.drop_duplicates(subset=["job_url"])
    after = len(df)
    
    if before > after:
        logger.info(f"Final deduplication removed {before - after} cross-source duplicates.")
        
    return df
