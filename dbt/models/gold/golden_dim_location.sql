{{ config(materialized='view', schema='gold') }}

SELECT
    ROW_NUMBER() OVER (ORDER BY location) AS location_sk,
    location,
    is_remote
FROM (
    SELECT DISTINCT
        location,
        is_remote
    FROM {{ ref('core_jobs') }}
) s