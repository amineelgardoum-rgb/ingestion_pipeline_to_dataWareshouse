SELECT
    COUNT(*)
FROM {{ ref('core_jobs') }}