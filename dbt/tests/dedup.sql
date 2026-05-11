with
    dedup
    AS
    (
        SELECT
            ROW_NUMBER () OVER(PARTITION BY job_url ORDER BY job_date) AS rank
        FROM {{ ref('core_jobs') }}

    )
SELECT 
    *
FROM dedup
WHERE rank > 1;