SELECT 
    COUNT(*) AS total_jobs_count
FROM {{ ref('core_jobs') }}
