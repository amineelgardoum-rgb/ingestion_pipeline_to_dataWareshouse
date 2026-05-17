from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk.bases.hook import BaseHook
from datetime import datetime
import pymssql


def test_db_connection():
    conn = BaseHook.get_connection("mssql_default")
    print(f"Connecting to: {conn.host} / {conn.schema}")

    try:
        connection = pymssql.connect(
            server=conn.host,
            user=conn.login,
            password=conn.password,
            database=conn.schema,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print(f"✅ Connection successful!")
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


with DAG(
    dag_id="test_db_connection",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["test", "db"],
) as dag:
    test_connection = PythonOperator(
        task_id="test_mssql_connection",
        python_callable=test_db_connection,
    )
