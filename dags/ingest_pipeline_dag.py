from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from src.utils.helpers import (
    test_db_connection,
    push_file_paths,
    read_file_paths,
    ingest_to_bronze,
)
from config.settings import PROCESSED_DIR, SOURCES
from src.pipeline import run_full_pipeline


with DAG(
    dag_id="ingest_pipeline",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ingest", "pipeline"],
) as dag:
    scrap = PythonOperator(
        task_id="scrape",
        python_callable=run_full_pipeline,
    )
    push = PythonOperator(
        task_id="push_processed_file_paths",
        python_callable=push_file_paths,
        op_kwargs={"processed_dir": str(PROCESSED_DIR)},
    )
    validate = PythonOperator(
        task_id="validate_processed_files",
        python_callable=read_file_paths,
    )
    test_db = PythonOperator(
        task_id="test_db_connection",
        python_callable=test_db_connection,
    )

    ingest_tasks = []
    for source in SOURCES:
        ingest_task = PythonOperator(
            task_id=f"ingest_{source}_to_bronze",
            python_callable=ingest_to_bronze,
            op_kwargs={"source": source},
        )
        ingest_tasks.append(
            ingest_task
        )  # here remember to append the tasks to the ingest_task list

    dbt_build = BashOperator(
        task_id="dbt_transformation",
        bash_command="cd /opt/airflow/dbt && /home/airflow/.local/bin/dbt clean && /home/airflow/.local/bin/dbt build --profiles-dir /opt/airflow/dbt",
    )

    scrap >> push >> validate >> test_db >> ingest_tasks >> dbt_build
