{% snapshot snap_silver_indeed %}

{{
    config(
        schema='snapshot',
        unique_key='job_url',
        strategy='check',
        check_cols=['location','job_type','is_remote']
        )
}}
SELECT 
    source,
    job_url,
    title,
    location,
    job_type,
    is_remote
FROM {{ ref('silver_indeed_jobs') }}
{% endsnapshot %}