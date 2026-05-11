{{config(materialized='view',schema='gold')}}
SELECT DISTINCT
    job_date ,
    DAY(job_date) AS day,
    MONTH(job_date) AS month,
    YEAR(job_date) AS year,
    DATEPART(QUARTER, job_date) AS quarter,
    DATENAME(WEEKDAY, job_date) AS weekday
FROM {{ref('core_jobs')}}