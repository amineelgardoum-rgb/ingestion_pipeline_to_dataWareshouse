import os
import logging
from pathlib import Path
from airflow.hooks.base import BaseHook
import pandas as pd
import pymssql
def clean_text(val):
    """Clean text by removing newlines, tabs, and collapsing multiple spaces."""
    if isinstance(val, str):
        val = val.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        val = ' '.join(val.split())
    return val

def get_project_root():
    """Returns the absolute path to the project root directory."""
    return Path(__file__).parent.parent.parent

def setup_logging(name="pipeline"):
    """Configures and returns a logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def push_file_paths(processed_dir,**context):
    """ this is a function that pushes the paths of the tsv files into a task to read them in order to save them into a db"""
    processed_dir=Path(processed_dir)
    paths={
        "indeed":str(processed_dir/"jobs_indeed_cleaned.tsv"),
        "linkedin":str(processed_dir/"jobs_linkedin_cleaned.tsv"),
        "rekrute":str(processed_dir/"jobs_rekrute_cleaned.tsv"),
        "emploi_ma":str(processed_dir/"jobs_emploi_ma_cleaned.tsv")
    }
    context['ti'].xcom_push(key="file_paths",value=paths)
    print(f"Pushed Paths:{paths}")

def read_file_paths(**context):
    """Read the path of the processed files in order to ingest data into the db """
    paths=context['ti'].xcom_pull(task_ids="push_processed_file_paths",key="file_paths")
    for source,path in paths.items():
        if os.path.exists(path):
            df=pd.read_csv(path,sep="\t")
            print(f"{source} : {len(df)} - rows - {path}.")
        else:
            print(f" {source} : file not found - {path}")


def test_db_connection():
    conn = BaseHook.get_connection("mssql_default")
    print(f"Connecting to: {conn.host} / {conn.schema}")

    try:
        connection = pymssql.connect(
            server=conn.host,
            user=conn.login,
            password=conn.password,
            database=conn.schema
        )
        cursor = connection.cursor()

        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print("✅ Connection successful!")
        print(f"SQL Server version: {row[0]}")

        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        tables = cursor.fetchall()
        print(f"📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")

        connection.close()

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        raise


def ingest_to_bronze(source, **context):
    paths = context['ti'].xcom_pull(task_ids="push_processed_file_paths",key="file_paths")
    path  = Path(paths[source])

    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    df = pd.read_csv(path, sep="\t")
    print(f"✅ {source}: {len(df)} rows loaded")

    # Get connection from Airflow
    conn = BaseHook.get_connection("mssql_default")
    connection = pymssql.connect(
        server=conn.host,
        user=conn.login,
        password=conn.password,
        database=conn.schema,
        port=str(conn.port)
    )
    cursor = connection.cursor()
    connection.commit()
    # here a check if the tables are in the datawarehouse , also check if there 
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'bronze') EXEC('CREATE SCHEMA bronze')")

    table = f"bronze.{source}_jobs"
    # Clear table before inserting fresh data
    cursor.execute(f"IF OBJECT_ID('{table}', 'U') IS NOT NULL TRUNCATE TABLE {table}")
    cols  = ", ".join([f"[{col}] NVARCHAR(MAX)" for col in df.columns])
    cursor.execute(f"""
        IF NOT EXISTS (
            SELECT * FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'bronze' AND TABLE_NAME = '{source}_jobs'
        )
        CREATE TABLE {table} ({cols})
    """)
    connection.commit()

    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_sql   = f"INSERT INTO {table} VALUES ({placeholders})"
    rows = [tuple(str(v) if pd.notna(v) else None for v in row) for _, row in df.iterrows()]
    cursor.executemany(insert_sql, rows)
    connection.commit()

    print(f"✅ Inserted {len(rows)} rows into {table}")
    connection.close()