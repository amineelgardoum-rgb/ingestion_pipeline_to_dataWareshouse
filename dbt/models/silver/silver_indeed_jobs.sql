{{ config(materialized='table', schema='silver') }}

SELECT
    CONVERT(
        NVARCHAR(100),
        HASHBYTES(
            'MD5',
            ISNULL(job_url, title + company + location)
        ),
        2
    ) AS job_sk,

    site AS source,

    job_url,

    job_url_direct,

    LOWER(
        LTRIM(RTRIM(
            REPLACE(
                REPLACE(
                    REPLACE(
                        CASE 
                            WHEN CHARINDEX(' - ', title) > 0 
                                THEN LEFT(title, CHARINDEX(' - ', title) - 1)
                            WHEN CHARINDEX(' | ', title) > 0 
                                THEN LEFT(title, CHARINDEX(' | ', title) - 1)
                            ELSE title
                        END,
                    '(H/F)', ''),
                'H/F', ''),
            'hf', '')
        ))
    ) AS title,

    company,

    CASE 
        WHEN location LIKE '%,%' 
            THEN LTRIM(RTRIM(LEFT(location, CHARINDEX(',', location) - 1)))
        ELSE LTRIM(RTRIM(location))
    END AS location,

    TRY_CONVERT(DATE, date_posted) AS job_date,

    CASE 
        WHEN job_type IS NULL THEN 'unknown'
        ELSE LOWER(LTRIM(RTRIM(job_type)))
    END AS job_type,

    CASE 
        WHEN is_remote = 'True' THEN 'Yes'
        WHEN is_remote = 'False' THEN 'No'
        ELSE 'Unknown'
    END AS is_remote,

    description

FROM {{ source('bronze','indeed_jobs') }}