# 📊 Basic ELT Pipeline (PostgreSQL + Python + Docker)

A modular, containerized **Extract, Load, Transform (ELT)** data pipeline built with Python, PostgreSQL, and Docker Compose. This project separates raw data ingestion from business transformation, mimicking real-world data warehouse architecture.

---

## 🏗️ Architecture Overview

[ ./data/raw_sales.csv ]
│
▼ (Step 1: Extract & Load)
[ PostgreSQL Schema: staging.raw_sales ]
│
▼ (Step 2: Transform via Python)
[ PostgreSQL Schema: analytics.daily_sales_summary ]


---

## 🛠️ Tech Stack
* **Containerization:** Docker & Docker Compose
* **Database & Warehouse:** PostgreSQL (15-alpine) with custom schemas (`staging` and `analytics`)
* **Management UI:** pgAdmin 4 (`http://localhost:8080`)
* **Pipeline Scripting:** Python 3.10, Pandas, SQLAlchemy, Psycopg2

---

## 📂 Project Structure


Basic_ELT_pipeline/
├── data/
│   └── raw_sales.csv            # Raw input dataset (simulating upstream source)
├── docker-compose.yaml          # Multi-container orchestration (db, etl_runner, pgadmin)
├── Dockerfile                   # Custom Python container definition for the ETL job
├── requirements.txt             # Python pipeline dependencies
├── init.sql                     # Database schema bootstrap script
└── pipeline.py                  # Core Python ELT script (load raw -> transform -> analytics)

