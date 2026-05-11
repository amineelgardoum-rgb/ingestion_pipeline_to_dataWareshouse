{{ config(materialized='view', schema='gold') }}

SELECT
    s.job_sk,
    d.job_date,
    l.location,
    jt.job_type,
    s.source,
    s.title,
    s.company,
    s.is_remote,
    s.description,
    s.job_url

FROM {{ ref('core_jobs') }} s

LEFT JOIN {{ ref('golden_dim_date') }} d
    ON d.job_date = s.job_date

LEFT JOIN {{ ref('golden_dim_location') }} l
    ON l.location = s.location

LEFT JOIN {{ ref('golden_dim_job_type') }} jt
    ON jt.job_type = s.job_type;