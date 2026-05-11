{% snapshot snap_silver_rekrute %}
{{
    config(
        schema='snapshot',
        unique_key='job_url',
        strategy='check',
        check_cols=['job_type','location','is_remote']
    )
}}
SELECT
    source,
    job_url,
    location,
    job_type,
    is_remote
FROM {{ ref('silver_rekrute_jobs') }}
{% endsnapshot %}
