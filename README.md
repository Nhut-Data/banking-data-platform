# 🏦 Banking Data Platform

A modular end-to-end **data engineering project** that simulates a real-world banking data ecosystem.  
It demonstrates scalable **ETL/ELT pipelines**, **data warehouse design**, and workflow orchestration using modern data engineering tools.

---

## 📌 Project Overview

The **Banking Data Platform** simulates a real banking system where multiple financial domains (customers, accounts, transactions, loans, etc.) are ingested, processed, and transformed into a structured **Data Warehouse on Google BigQuery**.

This project focuses on:
- End-to-end data pipeline design
- Domain-driven architecture
- Data warehouse modeling (Raw → Staging → Marts → Warehouse)
- Workflow orchestration with Airflow
- Data transformation using Python + dbt
- Cloud data warehouse integration (BigQuery)

---

## 🏗️ Architecture
CSV / SQLite (Data Sources)
↓
Python ETL (Initial Processing)
↓
BigQuery - Raw Layer
↓
dbt Transformations (Staging Layer)
↓
Data Marts Layer (Business Logic)
↓
Data Warehouse Layer (Final Aggregation)
↓
Analytics / Reporting Layer


---

## 🧱 Tech Stack

- Python (ETL processing)
- Apache Airflow (workflow orchestration)
- Docker / Docker Compose (containerization)
- Google BigQuery (data warehouse)
- SQLite (local data staging)
- dbt (data transformations)
- Kafka (event streaming simulation - optional/future)
- Pytest (testing framework)

---

## 📂 Project Structure

The project follows a **Domain-Driven Design (DDD)** approach:
src/
├── domains/
│ ├── customers/
│ ├── transactions/
│ ├── accounts/
│ ├── cards/
│ ├── loans/
│ ├── merchants/
│ ├── branches/
│
├── infrastructure/
│ ├── bigquery_client.py
│ ├── config.py
│ ├── logger.py
│
├── api/
└── tests/

Each domain contains:
- `extract.py` → data ingestion
- `transform.py` → transformation logic
- `load.py` → load into warehouse
- `schema.py` → data schema definition
- `repository.py` → data access layer

---

## 📊 Data Domains

| Domain        | Records |
|---------------|--------|
| Transactions  | 1,000,000 |
| Customers     | 50,000 |
| Accounts      | 75,000 |
| Cards         | 100,000 |
| Loans         | 30,000 |
| Merchants     | 5,000 |
| Branches      | 500 |

---

## ⚙️ Orchestration (Airflow)

- Apache Airflow is used to orchestrate all ETL workflows
- Each domain has independent DAG pipelines
- Supports scheduled batch ingestion
- Ensures modular and scalable pipeline execution

---

## 🧪 Testing Strategy

The project includes:

- Unit tests for transformation logic
- Integration tests for BigQuery connectivity
- Pytest-based testing framework
