

This repo serves as a hands-on workspace where I build, test, and containerize various data engineering concepts, architectural patterns, and workflow pipelines from scratch.

Rather than a single monolithic application, this repository is structured as a collection of **independent, modular mini-projects**, each designed to explore specific tools and methodologies in modern data engineering.

---

## 📂 Repository Structure

Each folder in this repository represents a standalone project focusing on a distinct concept:

| Project Directory | Core Concepts & Architecture | Tech Stack |
| :--- | :--- | :--- |
| **`Basic_ETL_pipeline/`** | Classic ETL pattern fetching live JSON data from a public REST API, transforming it via Pandas, and loading it into PostgreSQL. | Python, Requests, Pandas, SQLAlchemy, PostgreSQL, Docker Compose, pgAdmin |
| **`Advanced_ELT_pipeline/`** | Multi-tier ELT pattern separating raw CSV ingestion (`staging`) from business logic (`analytics`). Features automated schema initialization (`init.sql`) and bind mounts. | Python, Pandas, SQLAlchemy, PostgreSQL, Docker Compose, pgAdmin |
| **`(Future Projects)`** | Continuous Ingestion, Orchestration (Airflow/Prefect), Event Streaming (Kafka), Data Quality checks (Great Expectations). | *TBD* |

---

## 🛠️ General Tech Stack

Most projects in this repository utilize a standardized, modern local data stack containerized via Docker:
* **Orchestration / Containers:** Docker & Docker Compose
* **Databases / Warehouses:** PostgreSQL (with custom multi-schema architecture)
* **Ingestion & Transformation:** Python (Pandas, SQLAlchemy, PyArrow)
* **Management UIs:** pgAdmin 4
