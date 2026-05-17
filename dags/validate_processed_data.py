from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from config.settings import PROCESSED_DIR
from src.utils.helpers import push_file_paths, read_file_paths
from datetime import datetime

with DAG(
    dag_id="validate_processed_files",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["validate", "processed"],
) as dag:
    push = PythonOperator(
        task_id="push_processed_file_paths",
        python_callable=push_file_paths,
        op_kwargs={"processed_dir": PROCESSED_DIR},
    )
    pull = PythonOperator(
        task_id="pull_processed_file_paths", python_callable=read_file_paths
    )
    push >> pull
