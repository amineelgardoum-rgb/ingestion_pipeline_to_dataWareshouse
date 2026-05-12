{{ config(materialized='view', schema='gold') }}

SELECT
    s.job_sk,
    d.date_sk,
    l.location_sk,
    jt.job_type_sk,

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
    ON jt.job_type = s.job_type