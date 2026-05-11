{{ config(materialized='table', schema='silver') }}

WITH cte AS (
    SELECT *,
        CHARINDEX(' - ', REVERSE(title)) AS dash_pos
    FROM {{ source('bronze', 'emploi_ma_jobs') }}
    WHERE job_url LIKE 'http%'
),
cte2 AS (
    SELECT *,
        CASE 
            WHEN dash_pos = 0 THEN NULL
            ELSE LEN(title) - dash_pos
        END AS last_dash_pos
    FROM cte
),
deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY job_url ORDER BY date_posted DESC) AS rn
    FROM cte2
)
SELECT
    CONVERT(
        NVARCHAR(100),
        HASHBYTES('MD5', ISNULL(TRIM(job_url), title + company + location)),
        2
    )                                                                           AS job_sk,
    TRIM(source)                                                                AS source,
    TRIM(job_url)                                                               AS job_url,
    LOWER(TRIM(
        REPLACE(
        REPLACE(
        REPLACE(
            CASE 
                WHEN last_dash_pos IS NULL THEN TRIM(title)
                ELSE TRIM(LEFT(title, last_dash_pos - 1))
            END,
        '(H/F)', ''),
        'H/F', ''),
        'hf', '')
    ))                                                                          AS title,
    NULLIF(TRIM(company), '')                                                   AS company,
    TRIM(LEFT(location, CHARINDEX('-', location + '-') - 1))                   AS location,
    CAST(date_posted AS DATE)                                                   AS job_date,
    CASE 
        WHEN UPPER(TRIM(contract)) LIKE '%CDI%'       THEN 'CDI'
        WHEN UPPER(TRIM(contract)) LIKE '%CDD%'       THEN 'CDD'
        WHEN UPPER(TRIM(contract)) LIKE '%FREELANCE%' THEN 'FREELANCE'
        WHEN UPPER(TRIM(contract)) LIKE '%STAGE%'     THEN 'STAGE'
        WHEN UPPER(TRIM(contract)) LIKE '%INTÉRIM%'   THEN 'INTÉRIM'
        ELSE NULL
    END                                                                         AS job_type,
    CASE WHEN location LIKE '%International%' THEN 'Yes' ELSE 'No' END         AS is_remote,
    'Unknown'                                                                   AS description,
    TRIM(search_term)                                                           AS search_term
FROM deduped
WHERE rn = 1;