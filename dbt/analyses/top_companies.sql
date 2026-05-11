WITH cte_count_of_jobs_by_company AS (
    SELECT
        COUNT(*) AS count_of_jobs_by_company,
        company
    FROM {{ ref('core_jobs') }}
    GROUP BY company
)
SELECT 
    count_of_jobs_by_company,
    company
FROM cte_count_of_jobs_by_company
ORDER BY count_of_jobs_by_company DESC;