-- init.sql
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS staging.raw_sales (
    transaction_id VARCHAR(50),
    customer_id VARCHAR(50),
    transaction_date VARCHAR(50),
    amount VARCHAR(50),
    status VARCHAR(50),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.daily_sales_summary (
    sales_date DATE PRIMARY KEY,
    total_transactions INT,
    completed_transactions INT,
    total_revenue NUMERIC(10, 2),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);