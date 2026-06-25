# Banking Data Platform

Banking ETL pipeline: batch (5 CSV) + simulated streaming (SQLite -> Kafka) -> BigQuery.

Xem `docs/architecture.md` để biết kiến trúc đầy đủ, `docs/decisions/` cho
các quyết định thiết kế (ADR), `docs/data_dictionary.md` cho schema dữ liệu.

## Quick start

```bash
cp .env.example .env   # điền GCP_PROJECT_ID thật + đường dẫn service account key
make up                 # chạy docker compose, lên Airflow UI tại localhost:8080
```
kafka-ui localhost:8085
