import os
import time
import requests
import pandas as pd
from sqlalchemy import create_engine

# Read database connection parameters from environment variables
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "warehouse")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")


def extract_user_data(n_users=10):
    """EXTRACT: Fetch raw JSON payload from public REST API."""
    print(f"--> Extracting {n_users} user records from API...")
    url = f"https://randomuser.me/api/?results={n_users}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["results"]


def transform_user_data(raw_users):
    """TRANSFORM: Extract relevant fields and format into a structured DataFrame."""
    print("--> Transforming raw JSON payload into structured format...")
    transformed = []
    for u in raw_users:
        transformed.append({
            "user_id": u["login"]["uuid"],
            "first_name": u["name"]["first"],
            "last_name": u["name"]["last"],
            "gender": u["gender"],
            "country": u["location"]["country"],
            "email": u["email"],
            "ingested_at": pd.Timestamp.now()
        })
    return pd.DataFrame(transformed)


def load_data_to_postgres(df):
    """LOAD: Insert DataFrame into target PostgreSQL table."""
    connection_string = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # This line not only connects to PostgreSQL but also creates the 'raw_users' table if it doesn't exist. Automatically infers the schema from the DataFrame.
    engine = create_engine(connection_string)

    print("--> Connecting to PostgreSQL and writing data to 'raw_users' table...")
    # 'append' creates table if missing or appends new rows if present
    df.to_sql("raw_users", con=engine, if_exists="append", index=False)
    print("--> Load completed successfully!")


def main():
    # Retry mechanism to wait for PostgreSQL container startup
    time.sleep(5)

    raw_data = extract_user_data(n_users=10)
    clean_df = transform_user_data(raw_data)
    load_data_to_postgres(clean_df)


if __name__ == "__main__":
    main()
