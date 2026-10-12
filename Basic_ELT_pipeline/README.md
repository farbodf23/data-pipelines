# 🔄 Advanced Multi-Tier ELT Pipeline (PostgreSQL + Python + Docker)

An enterprise-grade **Extract, Load, Transform (ELT)** data pipeline that implements a multi-schema data warehouse architecture. This project separates raw, uncleaned ingestion data (`staging`) from business-ready aggregates (`analytics`) using a fully containerized Docker workflow.

---

## 🏗️ Architecture Overview

```text
[ ./data/raw_sales.csv ]
           │
           ▼ (Stage 1: Extract & Raw Load)
[ PostgreSQL Schema: staging.raw_sales ]
           │
           ▼ (Stage 2: Transform, Clean & Aggregate via Python)
[ PostgreSQL Schema: analytics.daily_sales_summary ]

```

---

## 📂 Project Structure

```text
Advanced_ELT_pipeline/
├── data/
│   └── raw_sales.csv            # Raw uncleaned CSV dataset mounted to container
├── docker-compose.yaml          # Multi-container stack (db, etl_runner, pgadmin)
├── Dockerfile                   # Custom Python container image definition
├── requirements.txt             # Python pipeline dependencies
├── init.sql                     # Database schema & table bootstrapping script
└── pipeline.py                  # Two-stage Python ELT script

```

---

## ⚙️ Technical Architecture & Implementation

### 1. Multi-Container Orchestration (`docker-compose.yaml`)

The stack manages three interconnected services inside an isolated virtual network:

* **`db` (PostgreSQL Warehouse):** Runs `postgres:15-alpine`. It maps port `5432` to the host, uses a persistent named volume (`pgdata`), and mounts `./init.sql` directly into `/docker-entrypoint-initdb.d/` to automatically bootstrap custom schemas on first startup. It also includes a native healthcheck (`pg_isready`).
* **`etl_runner` (Python ETL Job):** Built locally via the project’s `Dockerfile`. It mounts the local `./data` folder to `/app/data` inside the container so Python can seamlessly ingest local CSV files. It depends on `db` being healthy before booting.
* **`pgadmin` (Management Dashboard):** Runs `dpage/pgadmin4` mapped to local port `8080` for visual database inspection and query execution.

### 2. Database Schema Separation (`init.sql`)

To prevent table name collisions and enforce environment boundaries, the database is split into two custom schemas created on initialization:

* **`staging.raw_sales`:** Accepts raw string-typed incoming data directly from the CSV without strict type constraints.
* **`analytics.daily_sales_summary`:** Enforces strict production data types (`DATE` primary keys, `NUMERIC(10,2)` currency fields) for business reporting.

### 3. Optimized Dockerfile & Layer Caching

The custom image uses a lean multi-step build strategy:

* **Base Image:** Built on `python:3.10-slim`.
* **Layer Caching:** `requirements.txt` is copied and installed *before* the application code (`pipeline.py`), ensuring that modifying your pipeline script doesn't force Docker to reinstall pip dependencies from scratch.

### 4. Two-Stage Pipeline Logic (`pipeline.py`)

Executed via Python using **Pandas** and **SQLAlchemy**:

* **Stage 1 (Load Raw):** Reads `/app/data/raw_sales.csv`, truncates the staging table for a clean rerun, and bulk loads raw data into `staging.raw_sales`.
* **Stage 2 (Transform & Load Analytics):** Fetches staging data from PostgreSQL, applies data cleaning (filters only `COMPLETED` transactions, strips currency symbols, converts strings to floats/dates), aggregates daily revenue and transaction counts, and writes the final summary into `analytics.daily_sales_summary`.

---

## 🚀 Quick Start & Installation

1. Navigate into your project directory:
```bash
cd data-pipelines/Advanced_ELT_pipeline

```


2. Build and start the entire data stack in detached mode:
```bash
docker compose up --build -d

```


*(Note: If Postgres was previously run without `init.sql`, run `docker compose down -v` first to reset the volume).*
3. Monitor pipeline execution logs:
```bash
docker compose logs etl_runner

```


4. Query target tables directly using `psql` inside the container:
```bash
# Inspect Staging Raw Data
docker compose exec db psql -U postgres -d warehouse -c "SELECT * FROM staging.raw_sales;"

# Inspect Transformed Analytics Summary
docker compose exec db psql -U postgres -d warehouse -c "SELECT * FROM analytics.daily_sales_summary;"

```


5. Access the visual dashboard via **pgAdmin** at `http://localhost:8080` (Credentials: `admin@admin.com` / `root`).

---

## 🧹 Cleanup

To stop containers while keeping your database records:

```bash
docker compose down

```

To stop containers and completely wipe database volumes and schemas:

```bash
docker compose down -v

```

```

```
