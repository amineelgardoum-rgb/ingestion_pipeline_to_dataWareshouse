{%
   set source_jobs=[
    'silver_emploi_ma_jobs',
    'silver_indeed_jobs',
    'silver_rekrute_jobs'
   ]
%}
WITH cte_check_duplicates AS (
    {% for source in source_jobs %}
    SELECT
        COUNT(*) AS count_of_duplicates,
        job_url
    FROM {{ ref(source) }}
    GROUP BY job_url
    HAVING COUNT(*) >1
    {% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
)
SELECT 
    job_url
FROM cte_check_duplicates
WHERE count_of_duplicates >1;