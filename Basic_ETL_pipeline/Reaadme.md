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
🚀 Quick Start & Installation
Clone the repository and navigate into the project directory:

Bash
cd data-pipelines/Basic_ELT_pipeline
Build and run the entire data stack in detached mode:

Bash
docker compose up --build -d
Verify container execution and pipeline logs:

Bash
docker compose logs etl_runner
Inspect the data in PostgreSQL using the interactive CLI:

Bash
# Check Staging Table
docker compose exec db psql -U postgres -d warehouse -c "SELECT * FROM staging.raw_sales;"

# Check Transformed Analytics Table
docker compose exec db psql -U postgres -d warehouse -c "SELECT * FROM analytics.daily_sales_summary;"
Access the visual dashboard via pgAdmin at http://localhost:8080 (Credentials: admin@admin.com / root).

🧹 Cleanup
To stop containers while keeping your database volume intact:

Bash
docker compose down
To completely reset the pipeline, wipe the database volume, and clear staging/analytics tables:

Bash
docker compose down -v

<ElicitationsGroup message="What would you like to do next?">
  <Elicitation label="Add next mini-project documentation" query="Let's write the repository documentation or README for our next data pipeline project."/>
  <Elicitation label="Push local repository changes to GitHub" query="How do I add, commit, and push these README changes to my GitHub repository?"/>
</ElicitationsGroup>
