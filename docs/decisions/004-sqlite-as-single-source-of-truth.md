# ADR 004: SQLite là single source of truth, CSV bị loại bỏ

## Bối cảnh
Dataset có 6 entity tồn tại ở cả CSV lẫn SQLite, cộng thêm bảng
transactions chỉ có trong SQLite (1,000,000 rows).

## Kết quả kiểm tra (scripts/compare_csv_sqlite.py)
- account_id trong transactions overlap với SQLite accounts: 1000/1000 (100%)
- account_id trong transactions overlap với CSV accounts: 102/1000 (10.2%)
- branch_id: CSV và SQLite hoàn toàn khác nhau (generated độc lập)
- Tất cả entity: data khác nhau hoàn toàn giữa CSV và SQLite

## Quyết định
- SQLite là nguồn duy nhất cho toàn bộ project
- CSV bị loại bỏ hoàn toàn, không extract
- 6 entity tĩnh (accounts, customers, cards, loans, merchants, branches)
  → Airflow batch DAG đọc từ SQLite, load vào BigQuery (one-time + scheduled refresh)
- transactions → Producer giả lập streaming từ SQLite IDs → Kafka → Consumer
  → PostgreSQL buffer → Airflow hourly DAG → BigQuery

## Trade-off
- branches.city và branches.country trong SQLite đều NULL
  → Giữ cột trong schema để sau này có thể enrich, không drop
