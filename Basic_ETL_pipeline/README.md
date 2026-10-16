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

```text
Basic_ELT_pipeline/
├── data/
│   └── raw_sales.csv            # Raw input dataset (simulating upstream source)
├── docker-compose.yaml          # Multi-container orchestration (db, etl_runner, pgadmin)
├── Dockerfile                   # Custom Python container definition for the ETL job
├── requirements.txt             # Python pipeline dependencies
├── init.sql                     # Database schema bootstrap script
└── pipeline.py                  # Core Python ELT script (load raw -> transform -> analytics)
```
## ⚙️ Technical Architecture & Implementation

### 1. Multi-Container Orchestration (`docker-compose.yaml`)
The stack runs three interconnected services isolated inside a virtual bridge network:
* **`db` (PostgreSQL Warehouse):** Uses the lightweight `postgres:15-alpine` image. Maps port `5432` to the host machine for external querying and uses a persistent named volume (`pgdata`) to ensure data survives container restarts. It includes a native **healthcheck** (`pg_isready`) so other services know precisely when the database is ready to accept connections.
* **`etl_runner` (Python ETL Job):** Built locally via the project’s `Dockerfile`. It connects to the database using service-name resolution (`DB_HOST=db`) and uses `depends_on` with `condition: service_healthy` to guarantee it only starts *after* PostgreSQL is fully initialized.
* **`pgadmin` (Management UI):** Runs `dpage/pgadmin4` mapped to local port `8080`, providing a visual dashboard to inspect tables and run queries.

### 2. Optimized Dockerfile & Layer Caching
The custom image uses a multi-step build strategy designed for speed and efficiency:
* **Base Image:** Built on `python:3.10-slim` for a minimal footprint.
* **Layer Caching Optimization:** `requirements.txt` is copied and installed *before* the application source code (`pipeline.py`). This ensures that Docker caches dependency installation layers; editing your Python script won't force Docker to reinstall pip packages from scratch during rebuilds.

### 3. Pipeline Implementation (`pipeline.py`)
The Python script executes a classic ETL workflow using **Requests**, **Pandas**, and **SQLAlchemy**:
* **Extract:** Fetches live mock user JSON records from a public REST endpoint (`https://randomuser.me/api/`).
* **Transform:** Parses nested JSON structures using a Python loop, extracts core fields (UUID, name, gender, country, email), adds an `ingested_at` timestamp, and wraps the data into a clean Pandas DataFrame.
* **Load:** Establishes a connection to PostgreSQL using SQLAlchemy's connection string format. It utilizes `df.to_sql()` with `if_exists="append"` to automatically infer the database schema from the DataFrame and create the `raw_users` table on the fly if it does not yet exist.
