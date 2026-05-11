{% snapshot snap_emploi_ma_jobs %}

{{
    config(
        schema='snapshot',
        unique_key='job_url',
        strategy='check',
        check_cols=['job_type','location','is_remote'],

    )
}}
SELECT 
    source,
    job_url,
    company,
    location,
    job_type,
    is_remote
FROM {{ ref('silver_emploi_ma_jobs') }}
{% endsnapshot %}
