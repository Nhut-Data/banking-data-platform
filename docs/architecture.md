# Architecture Deep Dive

## Data Flow

### Batch Layer
1. SQLite → `extract_from_sqlite()` → raw DataFrame
2. Pydantic validation → drop invalid rows, log warnings
3. Write Parquet to `data/parquet_staging/` (intermediate, không dùng XCom)
4. Data quality gate (null/dup/range/row_count checks)
5. Load BigQuery raw → staging (SQL dedup) → warehouse (star schema)

### Streaming Layer
1. Producer reads reference IDs từ SQLite once at startup
2. Faker generates synthetic transactions every 2s với real timestamp
3. confluent-kafka publish với exponential backoff retry
4. Kafka Consumer polls micro-batch (30s / 100 msgs)
5. Pydantic validate → MERGE PostgreSQL (idempotent)
6. Airflow hourly DAG reads unprocessed rows → load BigQuery → mark processed

## Star Schema
fact_transaction

├── transaction_id (PK)

├── account_id (FK → dim_account)

├── merchant_id (FK → dim_merchant)

├── customer_id (FK → dim_customer)

├── amount_usd

├── transaction_date (PARTITION KEY)

└── _loaded_at
dim_customer: customer_id, full_name, email, city, credit_score, credit_score_band

dim_account:  account_id, customer_id, account_type, balance_usd, balance_band

dim_card:     card_id, account_id, card_type, expiration_date, is_expired

dim_loan:     loan_id, customer_id, loan_amount, interest_rate, loan_size_band

dim_merchant: merchant_id, merchant_name, city

dim_branch:   branch_id, branch_name, manager_name, city, country
## Idempotency Strategy

- **Batch**: `WRITE_TRUNCATE` — mỗi lần load ghi đè hoàn toàn raw table
- **Staging**: `QUALIFY ROW_NUMBER() OVER (PARTITION BY pk ORDER BY _ingested_at DESC) = 1` — dedup tự nhiên
- **Streaming (PostgreSQL)**: `INSERT ... ON CONFLICT (transaction_id) DO UPDATE` — MERGE pattern
- **Streaming (BigQuery)**: `WRITE_APPEND` + dedup ở staging layer

## Failure Handling

- **Producer**: retry exponential backoff 3 lần → DLQ topic `transactions.dlq`
- **Consumer**: Pydantic validation fail → DLQ, không crash consumer
- **Airflow**: `retries=2`, `retry_exponential_backoff=True`
- **Quality gate**: DAG fail ngay nếu quality check không pass, không load data bẩn
