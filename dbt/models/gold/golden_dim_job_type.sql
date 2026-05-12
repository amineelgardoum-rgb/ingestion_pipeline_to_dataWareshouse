{{ config(materialized='view',schema='gold') }}
SELECT ROW_NUMBER() OVER(ORDER BY job_type) AS job_type_sk,
    job_type
FROM (
SELECT DISTINCT job_type
    FROM {{ ref('core_jobs') }}
)s