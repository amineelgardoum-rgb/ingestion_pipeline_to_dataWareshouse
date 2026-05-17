import pyodbc
from config.config import (
    SQL_SERVER, SQL_DATABASE,
    SQL_USERNAME, SQL_PASSWORD,
    SQL_DRIVER, SQL_SCHEMA
)


def get_sql_connection() -> pyodbc.Connection:
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD};"
    )
    return pyodbc.connect(conn_str)


def get_jobs(conn: pyodbc.Connection) -> list[dict]:
    query = f"""
        SELECT
            DISTINCT
            f.job_sk,
            f.title,
            f.company,
            f.description,
            f.source,
            f.job_url,
            f.is_remote,
            l.location,
            jt.job_type,
            d.job_date,
            d.year,
            d.month
        FROM {SQL_SCHEMA}.golden_fact_jobs f
        LEFT JOIN {SQL_SCHEMA}.golden_dim_location l
            ON f.location_sk = l.location_sk
        LEFT JOIN {SQL_SCHEMA}.golden_dim_job_type jt
            ON f.job_type_sk = jt.job_type_sk
        LEFT JOIN {SQL_SCHEMA}.golden_dim_date d
            ON f.date_sk = d.date_sk
        WHERE f.description IS NOT NULL
          AND f.title      IS NOT NULL
    """
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return [
        {
            "job_id":      str(row[0]),
            "title":       row[1]        or "",
            "company":     row[2]        or "",
            "description": row[3]        or "",
            "source":      row[4]        or "",
            "job_url":     row[5]        or "",
            "is_remote":   row[6]        or "",
            "location":    row[7]        or "",
            "job_type":    row[8]        or "",
            "job_date":    str(row[9])   if row[9]  else "",
            "year":        str(row[10])  if row[10] else "",
            "month":       str(row[11])  if row[11] else "",
        }
        for row in rows
    ]


def close_sql_connection(conn: pyodbc.Connection) -> None:
    conn.close()