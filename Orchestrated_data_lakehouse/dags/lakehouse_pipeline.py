import os
from datetime import datetime

import pandas as pd
import boto3

from botocore.client import Config
from sqlalchemy import create_engine

from airflow import DAG
from airflow.operators.python import PythonOperator


# ==========================================
# Configuration
# ==========================================

AWS_ENDPOINT_URL = "http://localstack:4566"
AWS_REGION = "us-east-1"

BUCKET_NAME = "landing-zone"
S3_KEY = "raw_sales.parquet"

POSTGRES_CONNECTION = (
    "postgresql+psycopg2://postgres:postgres"
    "@postgres_warehouse:5432/warehouse"
)

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


# ==========================================
# S3 Client
# ==========================================

def get_s3_client():

    return boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        config=Config(signature_version="s3v4"),
    )


# ==========================================
# Task 1: Create bucket
# ==========================================

def create_s3_bucket():

    client = get_s3_client()

    try:

        client.head_bucket(
            Bucket=BUCKET_NAME
        )

        print(
            f"Bucket '{BUCKET_NAME}' already exists."
        )

    except Exception:

        print(
            f"Creating bucket '{BUCKET_NAME}'..."
        )

        client.create_bucket(
            Bucket=BUCKET_NAME
        )

        print(
            f"Bucket '{BUCKET_NAME}' created successfully."
        )


# ==========================================
# Task 2: Extract and land Parquet
# ==========================================

def extract_and_land_parquet():

    print("--> Extracting mock sales data...")

    data = {
        "transaction_id": [
            "TXN1001",
            "TXN1002",
            "TXN1003",
            "TXN1004"
        ],
        "customer_id": [
            "CUST_A",
            "CUST_B",
            "CUST_A",
            "CUST_C"
        ],
        "transaction_date": [
            "2026-10-01",
            "2026-10-01",
            "2026-10-02",
            "2026-10-02"
        ],
        "amount": [
            150.50,
            99.99,
            250.00,
            45.00
        ],
        "status": [
            "COMPLETED",
            "PENDING",
            "COMPLETED",
            "COMPLETED"
        ],
    }

    df = pd.DataFrame(data)

    file_path = "/tmp/raw_sales.parquet"

    print("--> Serializing DataFrame to Parquet...")

    df.to_parquet(
        file_path,
        engine="pyarrow",
        index=False
    )

    print("--> Uploading Parquet to S3...")

    client = get_s3_client()

    client.upload_file(
        file_path,
        BUCKET_NAME,
        S3_KEY
    )

    print("--> File successfully uploaded!")


# ==========================================
# Task 3: Transform and load
# ==========================================

def transform_and_load():

    client = get_s3_client()

    file_path = "/tmp/raw_sales.parquet"

    print("--> Downloading Parquet from S3...")

    client.download_file(
        BUCKET_NAME,
        S3_KEY,
        file_path
    )

    print("--> Reading Parquet...")

    df = pd.read_parquet(
        file_path,
        engine="pyarrow"
    )

    print("--> Transforming data...")

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"]
    )

    df["amount"] = df["amount"].astype(float)

    df["is_completed"] = (
        df["status"] == "COMPLETED"
    )

    print("--> Transformed data:")
    print(df)

    print("--> Connecting to PostgreSQL...")

    engine = create_engine(
        POSTGRES_CONNECTION
    )

    print("--> Loading data into PostgreSQL...")

    df.to_sql(
        "sales",
        engine,
        if_exists="replace",
        index=False
    )

    print("--> Data successfully loaded!")


# ==========================================
# DAG
# ==========================================

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}


with DAG(
    dag_id="lakehouse_landing_pipeline",

    default_args=default_args,

    description=(
        "Extract data, land Parquet in S3, "
        "transform it, and load PostgreSQL"
    ),

    schedule_interval=None,

    start_date=datetime(2026, 1, 1),

    catchup=False,

) as dag:

    task_create_bucket = PythonOperator(
        task_id="create_s3_bucket",
        python_callable=create_s3_bucket,
    )

    task_ingest_to_s3 = PythonOperator(
        task_id="extract_and_land_parquet",
        python_callable=extract_and_land_parquet,
    )

    task_transform_and_load = PythonOperator(
        task_id="transform_and_load",
        python_callable=transform_and_load,
    )

    task_create_bucket >> task_ingest_to_s3 >> task_transform_and_load
