{%
   set source_jobs=[
    'silver_emploi_ma_jobs',
    'silver_indeed_jobs',
    'silver_rekrute_jobs'
   ]
%}
WITH cte_check_date AS (
    {% for source in source_jobs %}
    SELECT
        job_url,
        job_date
    FROM {{ ref(source) }}
    WHERE job_date > CAST(GETDATE() AS DATE)
    {% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
)
SELECT 
    *
FROM cte_check_date;