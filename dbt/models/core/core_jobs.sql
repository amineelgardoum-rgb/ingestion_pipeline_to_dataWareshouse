{{ config(
    materialized='incremental',
    unique_key='job_sk',
    schema='silver'
) }}

-- =========================================================
-- LIST OF SILVER SOURCES TO BE COMBINED
-- Add new sources here (e.g. linkedin_jobs, glassdoor_jobs)
-- =========================================================
{% set job_sources = [
    'silver_emploi_ma_jobs',
    'silver_indeed_jobs',
    'silver_rekrute_jobs'
    
] %}

-- =========================================================
-- COMBINE ALL JOB SOURCES INTO ONE UNIFIED DATASET
-- =========================================================
WITH combined_jobs AS (

    {% for source in job_sources %}

        SELECT
            job_sk,        -- unique job identifier (defined in SILVER)
            source,        -- source system (indeed, rekrute, etc.)
            job_url,       -- original job URL
            title,         -- cleaned job title
            company,       -- company name
            location,      -- cleaned location
            job_date,      -- posting date
            job_type,     -- contract type
            is_remote ,     -- remote flag
            description    -- job description
        FROM {{ ref(source) }}

        -- Add UNION ALL between sources except last one
        {% if not loop.last %}
            UNION ALL
        {% endif %}

    {% endfor %}

),

-- =========================================================
-- REMOVE DUPLICATES BASED ON job_sk
-- KEEP MOST RECENT JOB ENTRY IF DUPLICATED
-- =========================================================
deduplicated AS (

    SELECT *
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY job_sk
                   ORDER BY job_date DESC
               ) AS rn
        FROM combined_jobs
    ) t
    WHERE rn = 1 -- here to choose the newer data 

)

-- =========================================================
-- FINAL OUTPUT OF CORE LAYER
-- =========================================================
SELECT
    job_sk,
    source,
    job_url,
    title,
    company,
    location,
    job_date,
    job_type,
    is_remote,
    description

FROM deduplicated

-- =========================================================
-- INCREMENTAL LOAD LOGIC
-- ONLY INSERT NEW JOBS NOT ALREADY IN TARGET TABLE
-- =========================================================
{% if is_incremental() %}

WHERE job_sk NOT IN (
    SELECT job_sk FROM {{ this }}
)

{% endif %}