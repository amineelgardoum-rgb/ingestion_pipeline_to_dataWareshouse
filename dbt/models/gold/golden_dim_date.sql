{{config(materialized='view',schema='gold')}}
SELECT
    ROW_NUMBER() OVER(ORDER BY job_date) as date_sk,
    job_date,
    day,
    month,
    year,
    quarter,
    weekday
FROM(
SELECT DISTINCT
    job_date ,
    DAY(job_date) AS day,
    MONTH(job_date) AS month,
    YEAR(job_date) AS year,
    DATEPART(QUARTER, job_date) AS quarter,
    DATENAME(WEEKDAY, job_date) AS weekday
FROM {{ref('core_jobs')}}
)s