# Banking Data Platform

![CI](https://github.com/Nhut-Data/banking-data-platform/actions/workflows/ci.yml/badge.svg)

End-to-end data engineering platform xử lý dữ liệu ngân hàng theo 2 luồng song song: **batch** (6 entity tĩnh) và **simulated streaming** (giao dịch real-time). Data chảy từ SQLite qua Kafka và Airflow vào BigQuery star schema, expose qua REST API.

---

## Architecture

SQLite (source of truth)

├── 6 entity tĩnh ──────────────────────────────────────────────────────┐

│   (accounts, customers, cards, loans, merchants, branches)             │

│   Airflow batch DAG (daily)                                            │

│   Extract → Validate (Pydantic) → Parquet → Load BigQuery raw         │

│                                                                        ▼

└── transactions (1M rows, dùng làm seed reference)          BigQuery

Producer (Faker + ref IDs, 1 tx/2s)                      ├── raw

→ Kafka topic transactions.events                         ├── staging (dedup, type cast)

→ Consumer (micro-batch 30s, MERGE idempotent)            ├── warehouse (star schema)

→ PostgreSQL raw_transactions buffer                       └── marts

→ Airflow hourly DAG (watermark: processed=FALSE)

→ BigQuery raw.transactions

│

▼

REST API (FastAPI)

/customers, /transactions
## Tech Stack

| Layer | Tool |
|---|---|
| Orchestration | Apache Airflow 3.2.2 (CeleryExecutor) |
| Streaming | Apache Kafka (KRaft), confluent-kafka |
| Data warehouse | Google BigQuery |
| Streaming buffer | PostgreSQL 16 |
| Transform | Pandas, SQL (BigQuery native) |
| Validation | Pydantic v2 |
| API | FastAPI |
| Containerization | Docker Compose (profiles: core/airflow/streaming) |
| CI/CD | GitHub Actions |
| Language | Python 3.12 |

## Dataset

Nguồn: SQLite database với 7 tables, tổng **1,260,500 rows**:

| Table | Rows | Role |
|---|---|---|
| transactions | 1,000,000 | Streaming source (seed reference) |
| accounts | 75,000 | Batch entity |
| customers | 50,000 | Batch entity |
| cards | 100,000 | Batch entity |
| loans | 30,000 | Batch entity |
| merchants | 5,000 | Batch entity |
| branches | 500 | Batch entity |

**Lưu ý:** 6 entity tĩnh cũng tồn tại dưới dạng CSV (được generate độc lập). Sau khi kiểm tra referential integrity (`scripts/compare_csv_sqlite.py`), xác nhận **SQLite là single source of truth** — transactions chỉ reference account_id/merchant_id từ SQLite (100% overlap), không phải CSV (10.2% overlap).

## Key Design Decisions

Xem `docs/decisions/` để đọc đầy đủ các ADR. Tóm tắt:

**[ADR-004] SQLite là single source of truth, CSV bị loại bỏ**
Verify bằng FK overlap test: transactions → SQLite accounts = 100%, transactions → CSV accounts = 10.2%.

**[ADR-003] Micro-batch load thay vì Streaming Insert API**
BigQuery Streaming Insert API có giới hạn cost và quota. Micro-batch (30s) đủ "near real-time" cho use case này, cost thấp hơn đáng kể.

**[ADR-001] Không dùng dbt**
Pipeline theo ETL pattern — transform bằng Pandas (validate/clean) trước khi load raw, heavy transform (star schema) chạy bằng SQL native trong BigQuery qua `BigQueryInsertJobOperator`. Không cần dbt làm thêm abstraction layer.

**[ADR-002] BigQuery thay vì Snowflake**
GCP free trial $300 credit, BigQuery serverless không cần quản lý cluster, SQL syntax quen thuộc hơn.

## Pipeline Details

### Batch Pipeline (Airflow DAG: `batch_pipeline`)

- Schedule: `@daily`
- 6 domain chạy **song song** (không phụ thuộc nhau)
- Mỗi domain: Extract SQLite → Validate Pydantic → Parquet → Load BigQuery raw
- Sau tất cả load: Data Quality Gate (null/duplicate/range/row_count checks)
- Intermediate storage: Parquet files (không truyền DataFrame qua XCom)

### Streaming Pipeline

- **Producer**: Đọc reference IDs từ SQLite 1 lần lúc startup, generate synthetic transactions bằng Faker mỗi 2 giây với `timestamp = NOW()`. Retry exponential backoff (1s → 2s → 4s), fail → DLQ.
- **Consumer**: Micro-batch poll Kafka mỗi 30 giây hoặc 100 messages. Validate Pydantic schema, invalid → DLQ. `MERGE` vào PostgreSQL theo `transaction_id` (idempotent, tránh at-least-once duplicate).
- **Airflow DAG `streaming_to_bq`**: Schedule `@hourly`, đọc `WHERE processed = FALSE`, load BigQuery, mark `processed = TRUE`. Watermark pattern đảm bảo không load lại data cũ.

### BigQuery Layers
raw          → data thô từ source, minimal transform

staging      → dedup (QUALIFY ROW_NUMBER), type cast, null filter

warehouse    → star schema: 6 dim tables + fact_transaction

PARTITION BY DATE(transaction_date)

CLUSTER BY account_id, merchant_id

marts        → aggregated views cho BI/API consumption
### Data Quality

Mỗi domain có quality gate riêng trước khi load BigQuery:
- Null check cho required columns (PK, FK)
- Duplicate check theo PK
- Range check cho numeric fields (credit_score: 300-850, balance_usd >= 0, interest_rate: 0-100)
- Row count check (tránh load empty dataset)

DAG fail ngay tại quality gate nếu bất kỳ check nào không pass — không load data bẩn lên warehouse.

## Performance & Cost

| Metric | Value |
|---|---|
| Batch pipeline runtime | ~21 giây (6 domains song song) |
| Streaming latency | ~30-32 giây (producer → PostgreSQL) |
| BigQuery raw rows | 260,590 (6 entity) + 90 transactions |
| Unit test runtime | 0.57 giây (31 tests) |
| Estimated BigQuery cost | ~$0/tháng ở scale demo (free tier: 1TB query/tháng) |

## Quick Start

```bash
# 1. Clone repo
git clone https://github.com/Nhut-Data/banking-data-platform.git
cd banking-data-platform

# 2. Setup environment
cp .env.example .env
# Điền GCP_PROJECT_ID trong .env

# 3. Authenticate GCP
gcloud auth application-default login
gcloud auth application-default set-quota-project <your-project-id>

# 4. Đặt data files
# Copy bank_sqlite.db vào data/raw/sqlite/

# 5. Start core services (Postgres, Redis, Kafka)
make up

# 6. Start Airflow
make init   # chạy 1 lần
make airflow

# 7. Start streaming (optional)
make streaming

# 8. Trigger batch pipeline
# Vào http://localhost:8080 → batch_pipeline → Trigger

# 9. Start API
uv run uvicorn src.api.main:app --port 8090
# Swagger UI: http://localhost:8090/docs
```

## Project Structure
banking-data-platform/

├── airflow/dags/

│   ├── ingestion/          # batch_pipeline_dag.py, streaming_to_bq_dag.py

│   ├── transformation/     # SQL transform DAGs (placeholder)

│   ├── quality/            # Quality monitoring DAGs (placeholder)

│   └── monitoring/

├── src/

│   ├── infrastructure/     # config, logger, bigquery_client, postgres_client

│   │   ├── pipeline.py     # Generic ETL pipeline (DRY pattern)

│   │   └── quality.py      # Data quality checks

│   ├── domains/

│   │   └── configs.py      # Single source of truth cho 6 domain schemas

│   ├── streaming/

│   │   ├── producer.py     # Kafka producer (Faker + confluent-kafka)

│   │   ├── consumer.py     # Kafka consumer (micro-batch, MERGE)

│   │   └── schemas.py      # TransactionEvent Pydantic schema

│   └── api/                # FastAPI REST API

├── sql/

│   ├── raw/                # BigQuery raw DDL

│   ├── staging/            # Staging transforms (dedup, type cast)

│   └── warehouse/          # Star schema DDL (dims + facts)

├── tests/unit/             # 31 unit tests

├── docs/decisions/         # Architecture Decision Records (ADR)

└── docker-compose.yaml     # Profiles: core / airflow / streaming
## API Endpoints

Base URL: `http://localhost:8090`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/customers/` | List customers (filter by city, credit_score_band) |
| GET | `/customers/{id}` | Get customer by ID |
| GET | `/transactions/daily-summary` | Daily transaction summary |
| GET | `/transactions/by-account/{id}` | Transactions by account |

Swagger UI: `http://localhost:8090/docs`

## Tests & CI

```bash
# Run unit tests
make test

# Run linter
make lint

# CI runs automatically on every push to main
```

31 unit tests covering: pipeline validation, Pydantic schemas, data quality checks.
