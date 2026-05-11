{% snapshot snap_core_jobs %}
{{
    config(
        schema='snapshot',
        unique_key='job_url',
        strategy='check',
        check_cols=['job_type','location','is_remote','source']
    )
}}
SELECT 
   source,
   job_url,
   title,
   is_remote,
   job_type,
   location
FROM {{ ref('core_jobs') }}
{% endsnapshot %}