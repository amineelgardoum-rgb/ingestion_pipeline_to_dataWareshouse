# Data Warehouse Project: Job Market Analytics (dbt)

This project implements a modular Data Warehouse architecture using **dbt (data build tool)** to process and analyze job postings scraped from various sources (**Emploi.ma**, **Rekrute**, and **Indeed**).

## 🏗 Architecture Overview

The project follows the **Medallion Architecture** (Bronze, Silver, Gold layers) to ensure data quality and maintainability:

1.  **Bronze Layer (Raw)**: Raw data loaded by scrapers into the `bronze` schema.
2.  **Silver Layer (Cleansing)**: Standardizes schemas, cleans job titles, normalizes locations/contract types, and hashes unique keys (`job_sk`).
3.  **Core Layer (Integration)**: Unifies all Silver models into a single, deduplicated incremental table (`core_jobs`).
4.  **Gold Layer (Presentation)**: Star schema optimized for BI, consisting of dimension tables and a central fact table (`golden_fact_jobs`).
5.  **Snapshot Layer**: Implements Slowly Changing Dimensions (SCD Type 2) to track changes in job postings over time.

---

## 📁 Project Structure

```text
dbt/
├── models/
│   ├── silver/      # Data cleansing & standardization
│   ├── core/        # Unified incremental core table
│   ├── gold/        # Star schema (Fact & Dimensions)
│   └── sources.yml  # Source definitions for bronze data
├── snapshots/       # SCD Type 2 tracking
├── analyses/        # Ad-hoc SQL queries
├── tests/           # Data quality assertions
├── macros/          # Reusable SQL logic
└── dbt_project.yml  # Project configuration
```

---

## 🚀 Key Components

### 1. Data Cleaning (Silver Layer)
Each source has a dedicated Silver model (e.g., `silver_emploi_ma_jobs`) that performs:
- **Title Normalization**: Removes "H/F" tags and city names from titles.
- **Location Standardizing**: Extracts primary city.
- **Contract Normalization**: Maps raw strings to standard types (CDI, CDD, Freelance, etc.).
- **Surrogate Keys**: Generates `job_sk` using MD5 hashing of `job_url`.

### 2. Unified Core (`core_jobs`)
An **incremental** model that combines all sources. It uses dbt's Jinja templating to iterate over sources and handles deduplication by keeping the most recent entry for each `job_sk`.

### 3. Star Schema (Gold Layer)
- **`golden_fact_jobs`**: Central fact table for analytics.
- **Dimensions**: `golden_dim_date`, `golden_dim_location`, `golden_dim_job_type`.

### 4. Snapshots
Snapshots (e.g., `snap_core_jobs`) track changes in job attributes like `location` or `job_type` using the `check` strategy, allowing for historical trend analysis.

---

## 🛠 Usage

### Prerequisites
- dbt Core installed.
- Database connection configured in `profiles.yml`.

### Run Commands
```bash
# Install dependencies
dbt deps

# Run all models
dbt run

# Run snapshots
dbt snapshot

# Execute data quality tests
dbt test

# Generate and view documentation site
dbt docs generate
dbt docs serve
```

---

## 📊 Data Quality Tests
Custom tests are located in `/tests` to ensure:
- Unique surrogate keys.
- Dates are not in the future.
- Deduplication logic is working as expected.

---

## 🔍 Analytics Examples
Check the `/analyses` folder for pre-written queries:
- `top_companies.sql`: Companies with the most job postings.
- `count_of_jobs.sql`: Total job volume across sources.
