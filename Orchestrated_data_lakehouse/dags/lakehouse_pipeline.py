import os
from datetime import datetime
import pandas as pd
import boto3
from botocore.client import Config
from airflow import DAG
from airflow.operators.python import PythonOperator

# --- S3 / LocalStack Configuration ---
# Inside Docker, use the service name 'localstack'. Port 4566 is the LocalStack gateway.
AWS_ENDPOINT_URL = "http://localstack:4566"
AWS_REGION = "us-east-1"
BUCKET_NAME = "landing-zone"

# LocalStack dummy credentials
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


def get_s3_client():
    """Creates a boto3 S3 client pointed to LocalStack."""
    return boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        config=Config(signature_version="s3v4"),
    )


def create_s3_bucket():
    """Step 2: Ensure the raw landing zone bucket exists in LocalStack S3."""
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=BUCKET_NAME)
        print(f" Bucket '{BUCKET_NAME}' already exists.")
    except Exception:
        print(f" Creating bucket '{BUCKET_NAME}'...")
        client.create_bucket(Bucket=BUCKET_NAME)
        print(f" Bucket '{BUCKET_NAME}' created successfully.")


def extract_and_land_parquet():
    """Step 3: Extract data, serialize to Parquet, and upload to S3."""
    print("--> Extracting mock sales data...")

    # Simulated raw data (mimicking a upstream source)
    data = {
        "transaction_id": ["TXN1001", "TXN1002", "TXN1003", "TXN1004"],
        "customer_id": ["CUST_A", "CUST_B", "CUST_A", "CUST_C"],
        "transaction_date": ["2026-10-01", "2026-10-01", "2026-10-02", "2026-10-02"],
        "amount": [150.50, 99.99, 250.00, 45.00],
        "status": ["COMPLETED", "PENDING", "COMPLETED", "COMPLETED"],
    }
    df = pd.DataFrame(data)

    # Define local path for temporary parquet file staging
    file_path = "/tmp/raw_sales.parquet"

    # Serialize DataFrame into columnar Parquet format using pyarrow
    print("--> Serializing DataFrame to Parquet format...")
    df.to_parquet(file_path, engine="pyarrow", index=False)

    # Upload to LocalStack S3
    print(f"--> Uploading {file_path} to S3 bucket '{BUCKET_NAME}'...")
    client = get_s3_client()
    client.upload_file(file_path, BUCKET_NAME, "raw_sales.parquet")
    print("--> File successfully landed in object storage!")


# --- Airflow DAG Definition ---
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="lakehouse_landing_pipeline",
    default_args=default_args,
    description="An ELT pipeline that lands raw data as Parquet into LocalStack S3",
    schedule_interval=None,  # Trigger manually for now
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    task_create_bucket = PythonOperator(
        task_id="create_s3_bucket", python_callable=create_s3_bucket
    )

    task_ingest_to_s3 = PythonOperator(
        task_id="extract_and_land_parquet",
        python_callable=extract_and_land_parquet,
    )

    # Define task execution order
    task_create_bucket >> task_ingest_to_s3
