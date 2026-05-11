# Jobs Data Pipeline & Data Warehouse Project

This project is a multi-source data pipeline designed to scrape, clean, and store job listings from various platforms (Indeed, Rekrute, Emploi.ma, LinkedIn) into a structured Data Warehouse format.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [Data Sources](#data-sources)
4. [Data Layers](#data-layers)
5. [Getting Started](#getting-started)
6. [Data Schema (Bronze Layer)](#data-schema-bronze-layer)

---

## Project Overview

The goal of this project is to automate the collection of job postings for specific search terms (e.g., "Data Engineer", "Data Scientist", "Data Analyst") in Morocco. The collected data is processed through a cleaning pipeline and prepared for ingestion into a Data Warehouse. <!-- rumdl-disable-line MD013 -->

## Pipeline Architecture

The pipeline follows a modular design:
- **Ingestion (Scrapers):** Using `python-jobspy` and custom collectors to fetch data from multiple job boards.
- **Raw Storage:** Data is saved as TSV files in `data/raw/` to preserve the original state.
- **Transformation (Cleaning):** Text sanitization, deduplication, and column standardization using `pandas`.
- **Processed Storage:** Cleaned data is saved in `data/processed/` for warehouse ingestion.

## Data Sources
- **Indeed:** Full-featured scraping including salary, company details, and descriptions.
- **LinkedIn:** Comprehensive professional listings.
- **Rekrute:** Morocco-focused job board.
- **Emploi.ma:** Localized job board with specific contract types.

## Data Layers

1. **Bronze (Raw/Staging):** Stores the processed TSV files as-is. Minimal transformation, focuses on ingestion speed and data preservation.
2. **Silver (Cleaned/Standardized):** (Next Phase) Unified schema across all sources, standardized locations, and job category mapping.
3. **Gold (Analytics):** (Next Phase) Aggregated data for reporting, trend analysis, and market insights.

---

## Getting Started

### Prerequisites
- Python 3.12+
- `pip install pandas python-jobspy python-dotenv`

### Running the Pipeline
```bash
python -m src.pipeline
```
This will:
1. Load search terms and locations from `config/settings.py`.
2. Scrape data from all enabled sources.
3. Save raw files to `data/raw/`.
4. Clean the data and save processed files to `data/processed/`.

---

## Data Schema (Bronze Layer)

The Bronze layer in the Data Warehouse should accommodate the varying schemas of our sources. Below is the recommended DDL for the combined Bronze table or individual staging tables.

### Unified Bronze Table DDL (Example for PostgreSQL/Snowflake)

Since `Indeed` and `LinkedIn` provide more metadata than `Rekrute` and `Emploi.ma`, a flexible schema is used.

```sql
CREATE TABLE bronze_jobs (
    -- Primary Keys & Identifiers
    id VARCHAR(255),
    source VARCHAR(50),          -- 'indeed', 'linkedin', 'rekrute', 'emploi_ma'
    site VARCHAR(50),
    job_url TEXT,
    job_url_direct TEXT,
    
    -- Job Details
    title TEXT,
    company TEXT,
    location TEXT,
    date_posted DATE,
    job_type VARCHAR(100),
    job_level VARCHAR(100),
    job_function TEXT,
    contract VARCHAR(100),       -- Specific to Emploi.ma
    
    -- Salary Info (Mostly Indeed/LinkedIn)
    min_amount FLOAT,
    max_amount FLOAT,
    currency VARCHAR(10),
    interval VARCHAR(20),
    
    -- Company Details
    company_industry TEXT,
    company_url TEXT,
    company_description TEXT,
    company_num_employees VARCHAR(100),
    company_revenue VARCHAR(100),
    
    -- Content
    description TEXT,
    skills TEXT,
    experience_range TEXT,
    
    -- Metadata
    search_term VARCHAR(255),
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

> **Note on DDL Correction:**
> After reviewing the processed data columns:
> - **Indeed/LinkedIn** have ~36 columns including deep company metadata.
> - **Rekrute/Emploi.ma** have only ~7-8 columns.
> - **Recommendation:** Ensure your DDL uses `NULL` for missing columns when ingesting from Rekrute/Emploi.ma. The `source` column is critical for partitioning and troubleshooting.
