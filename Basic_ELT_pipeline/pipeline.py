import os
import pandas as pd
from sqlalchemy import create_engine, text

# 1. Database Connection String
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "warehouse")
# Creating SQLAlchemy Engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)


def load_raw_data():
    # Using pandas tor read the csv.
    print("📥 [STAGE 1] Loading raw CSV into staging.raw_sales...")
    df_raw = pd.read_csv('/app/data/raw_sales.csv')

    # Truncate staging table for clean rerun
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE staging.raw_sales;"))
        conn.commit()

    # Load raw dataframe into PostgreSQL staging table
    df_raw.to_sql(
        name='raw_sales',
        con=engine,
        schema='staging',
        if_exists='append',
        index=False
    )
    print(f"✅ Loaded {len(df_raw)} raw rows into staging.raw_sales.")


def transform_and_load_analytics():
    """Transforms raw staging data and loads into analytics.daily_sales_summary."""
    print("🔄 [STAGE 2] Transforming data from staging to analytics...")

    # Fetch raw data from Postgres staging table
    query = "SELECT * FROM staging.raw_sales;"
    df_staging = pd.read_sql(query, con=engine)

    # --- Data Cleaning & Transformation ---
    # 1. Filter out non-completed transactions
    df_clean = df_staging[df_staging['status'] == 'COMPLETED'].copy()

    # 2. Clean amount column (remove '$' and convert to float)
    df_clean['amount'] = df_clean['amount'].astype(
        str).str.replace('$', '', regex=False).astype(float)

    # 3. Convert transaction_date to datetime
    df_clean['transaction_date'] = pd.to_datetime(df_clean['transaction_date'])

    # 4. Aggregate: Daily Revenue & Counts
    summary = df_clean.groupby('transaction_date').agg(
        total_transactions=('transaction_id', 'count'),
        completed_transactions=('transaction_id', 'count'),
        total_revenue=('amount', 'sum')
    ).reset_index()

    summary.rename(columns={'transaction_date': 'sales_date'}, inplace=True)

    # --- Write to Target Analytics Table ---
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.daily_sales_summary;"))
        conn.commit()

    summary.to_sql(
        name='daily_sales_summary',
        con=engine,
        schema='analytics',
        if_exists='append',
        index=False
    )
    print("✅ Transformation complete. Aggregated analytics data written to analytics.daily_sales_summary:")
    print(summary)


if __name__ == "__main__":
    load_raw_data()
    transform_and_load_analytics()
