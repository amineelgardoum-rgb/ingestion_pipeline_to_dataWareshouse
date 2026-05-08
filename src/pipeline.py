import pandas as pd
from pathlib import Path
from src.collectors import indeed, rekrute,emploi_ma, linkedin
from src.transformers import cleaner
from src.utils.helpers import setup_logging

logger = setup_logging("pipeline")

def run_full_pipeline():
    """Orchestrates the end-to-end data pipeline."""
    project_root = Path(__file__).parent.parent
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    collectors = [
        ("indeed", indeed),
        ("rekrute", rekrute),
        ("emploi_ma", emploi_ma),
        ("linkedin", linkedin)
    ]
    
    for name, module in collectors:
        try:
            logger.info(f"--- Running {name} collector ---")
            df = module.collect()
            
            if not df.empty:
                # 1. Save raw data
                raw_path = raw_dir / f"jobs_{name}_raw.tsv"
                df.to_csv(raw_path, sep="\t", index=False, encoding="utf-8")
                logger.info(f"Saved raw {name} data to {raw_path}")
                
                # 2. Clean and save processed data separately
                logger.info(f"Cleaning {name} data...")
                cleaned_df = cleaner.clean_data(df)
                processed_path = processed_dir / f"jobs_{name}_cleaned.tsv"
                cleaned_df.to_csv(processed_path, sep="\t", index=False, encoding="utf-8")
                logger.info(f"Saved cleaned {name} data to {processed_path}")
            else:
                logger.warning(f"No data collected from {name}")
                
        except Exception as e:
            logger.error(f"Pipeline failed for {name}: {e}")

    logger.info("--- Scraping Pipeline Completed Successfully ---")

if __name__ == "__main__":
    run_full_pipeline()
