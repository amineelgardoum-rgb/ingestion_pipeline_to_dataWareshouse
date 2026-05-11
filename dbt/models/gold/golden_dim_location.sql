{{config(materialized='view',schema='gold')}}
SELECT DISTINCT
    location ,
    is_remote
FROM {{ref('core_jobs')}};
 