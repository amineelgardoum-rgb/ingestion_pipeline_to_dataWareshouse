# Jobs Data Warehouse Project

An end-to-end data engineering pipeline that scrapes job listings from multiple sources, cleans the data, and transforms it into a multi-layered data warehouse using Airflow, dbt, and MS SQL Server.

## 🚀 Project Architecture

The project follows a modern data stack architecture:

1.  **Collection Layer**: Custom scrapers (Indeed, LinkedIn, Rekrute, Emploi.ma) collect raw job data using Python and JobSpy.
2.  **Orchestration Layer**: Apache Airflow manages the entire workflow, dependencies, and scheduling.
3.  **Data Warehouse (MS SQL Server)**:
    *   **Bronze (Raw)**: Landing area for raw data ingested from TSV files.
    *   **Silver (Staging)**: Cleaned and standardized data across all sources (handled by dbt).
    *   **Core (Integration)**: Unified job listings with deduplication and source merging (handled by dbt incremental models).
    *   **Gold (Analytics)**: Dimensional models (Fact & Dimension tables) optimized for BI and analysis (Star Schema).
4.  **Monitoring Layer**: Prometheus and StatsD for metrics, Grafana for visualization of Airflow and pipeline health.

## 📁 Project Structure

```text
├── config/             # Airflow, Prometheus, and StatsD configuration
├── dags/               # Airflow DAG definitions (Ingest & Transformation)
├── data/               # Local storage for raw and processed TSV data
├── dbt/                # dbt project (models, macros, tests, snapshots)
│   ├── models/
│   │   ├── silver/     # Source-specific cleaning & staging
│   │   ├── core/       # Incremental unified job table
│   │   └── gold/       # Star schema (Fact/Dims)
├── docker/             # Docker configuration (Dockerfile & Compose)
├── docs/               # Project documentation, diagrams, and PDFs
├── notebooks/          # Scraper development and data exploration
├── scripts/            # Utility scripts for discovery and validation
├── src/                # Core Python logic (collectors, transformers, pipeline)
└── requirements-docker.txt # Python dependencies for the container
```

## 🐳 Docker Services

The project is fully containerized with the following services in the `docker-compose.yaml`:

| Service | Description | Port |
| :--- | :--- | :--- |
| **Airflow API Server** | The web interface and API for Airflow. | `8080` |
| **Airflow Scheduler** | Monitors tasks and triggers DAG runs. | - |
| **Airflow Worker** | Executes the tasks (Scraping, DB Ingestion, dbt). | - |
| **Airflow Triggerer** | Handles asynchronous/deferred operations. | - |
| **Airflow DAG Processor**| Separated process for parsing DAG files. | - |
| **Airflow Init** | One-time setup service (DB migrations, admin user). | - |
| **PostgreSQL** | Metadata database for Airflow state. | `5432` |
| **Redis** | Broker for Airflow Celery executor. | `6379` |
| **Flower** | Monitoring UI for Celery workers. | `5555` |
| **dbt-docs** | Serves the generated dbt project documentation. | `8082` |
| **Prometheus** | Time-series database for system and pipeline metrics. | `9090` |
| **Grafana** | Dashboarding tool connected to Prometheus. | `3000` |
| **StatsD Exporter** | Maps Airflow StatsD metrics to Prometheus format. | `9102` |

## 🛠️ Data Pipeline Workflow (Airflow DAG)

The main `ingest_pipeline` DAG orchestrates the following flow:

1.  **Scrape**: Executes Python scrapers via `src.pipeline.run_full_pipeline`, saving raw TSVs and cleaning them.
2.  **Push/Validate**: Tracks processed file paths using Airflow Variables/XComs and validates schema.
3.  **Test DB**: Ensures the target MS SQL Server warehouse is reachable.
4.  **Ingest to Bronze**: Loads the cleaned data from TSV files into the `bronze` schema in SQL Server.
5.  **dbt Transformation**: Triggers `dbt build`, which runs all models (Silver -> Core -> Gold), executes data tests, and creates snapshots.

## 📊 Transformation Layers (dbt)

*   **Silver**: Standardizes column names, handles nulls, and casts data types for each source (Indeed, LinkedIn, etc.).
*   **Core**: Consolidates all jobs into a single `core_jobs` table using an **Incremental** strategy to handle updates and prevent duplicates.
*   **Gold**: Implements a Star Schema for analytics:
    *   `golden_fact_jobs`: Central fact table with job metrics.
    *   `golden_dim_location`: Normalized location data.
    *   `golden_dim_job_type`: Normalized job categories.
    *   `golden_dim_date`: Time dimension for trend analysis.

## 🚦 Getting Started

1.  **Environment Variables**: Create a `.env` file in the project root with your database credentials and Airflow secrets.
2.  **Launch Stack**:
    ```bash
    docker-compose -f docker/docker-compose.yaml up --build
    ```
3.  **Access UIs**:
    *   **Airflow**: [http://localhost:8080](http://localhost:8080) (Default: `airflow/airflow`)
    *   **Grafana**: [http://localhost:3000](http://localhost:3000) (Default: `admin/admin`)
    *   **dbt Documentation**: [http://localhost:8082](http://localhost:8082)
