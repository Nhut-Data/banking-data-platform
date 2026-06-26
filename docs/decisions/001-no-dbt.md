# ADR 001: Không dùng dbt

## Quyết định
Dùng SQL files native chạy qua BigQueryInsertJobOperator thay vì dbt.

## Lý do
- Pipeline theo ETL pattern — transform Pandas trước khi load raw
- Heavy transform (star schema) chạy SQL trực tiếp trong BigQuery
- Không cần thêm dbt abstraction layer, giảm complexity
- Airflow đã đủ để orchestrate SQL transform theo thứ tự dependency

## Trade-off
- Không có dbt docs, dbt test, lineage graph tự động
- SQL files phải tự manage dependency thứ tự chạy
