{{config(materialized='view',schema='gold')}}
SELECT DISTINCT job_type 
FROM {{ref('core_jobs')}}