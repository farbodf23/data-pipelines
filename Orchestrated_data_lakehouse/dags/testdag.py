from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}


def heavy_path():
    print("kir to amin")


def light_path():
    print("kir to ali")


def choose_branch(**context):
    """Evaluates a condition at runtime and returns the ID of the next task."""
    # In a real pipeline, this could check an S3 file size, a row count, or an API flag.
    # For this example, let's simulate a random condition or a variable check.
    data_volume_is_large = False  # Change to False to test the other branch

    if data_volume_is_large:
        print("--> Condition met: Routing to heavy processing pipeline.")
        return "process_large_dataset"
    else:
        print("--> Condition met: Routing to lightweight processing pipeline.")
        return "process_small_dataset"


with DAG(
    dag_id="branching_pipeline_example",
    default_args=default_args,
    description="An example of dynamic branching in Apache Airflow",
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # 1. Starting task
    start_task = EmptyOperator(task_id="start_pipeline")

    # 2. The Branch Operator
    branch_task = BranchPythonOperator(
        task_id="evaluate_data_condition", python_callable=choose_branch
    )

    # 3. Possible downstream branch paths
    path_heavy = PythonOperator(
        task_id="process_large_dataset", python_callable=heavy_path)
    path_light = PythonOperator(
        task_id="process_small_dataset", python_callable=light_path)

    # 4. Re-converging task (uses trigger_rule='none_failed_min_one_success' by default in modern Airflow)
    join_task = EmptyOperator(
        task_id="finalize_pipeline", trigger_rule="none_failed")

    # Define the workflow graph
    start_task >> branch_task
    branch_task >> [path_heavy, path_light]
    [path_heavy, path_light] >> join_task
