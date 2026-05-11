{{ config(materialized='table', schema='silver') }}

SELECT
    CONVERT(
        NVARCHAR(100),
        HASHBYTES('MD5', ISNULL(job_url, title + company + location)),
        2
    ) AS job_sk,

    source,
    job_url,

    -- clean title
    LOWER(
        LTRIM(RTRIM(
            REPLACE(REPLACE(title, '(H/F)', ''), '(F/H)', '')
        ))
    ) AS title,

    company,

    LOWER(
        LTRIM(RTRIM(location))
    ) AS location,

    TRY_CONVERT(DATE, date_posted) AS job_date,

    job_type,
    'Unknown' AS is_remote,
    'Unknown' AS description

FROM {{ source('bronze','rekrute_jobs') }}