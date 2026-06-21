"""
Extract layer cho domain transactions.

LƯU Ý QUAN TRỌNG: domain này KHÔNG dùng pattern batch CSV như 6 domain còn lại.
Nguồn dữ liệu là SQLite table `transactions`, được mô phỏng streaming qua:
  scripts/producer.py  -> đọc SQLite, publish vào Kafka topic transactions.events
  (consumer service riêng, KHÔNG chạy trong Airflow) -> đọc Kafka micro-batch,
  load vào BigQuery raw.transactions với MERGE theo transaction_id (idempotent)

File này giữ lại để đồng nhất cấu trúc domain, không dùng trong luồng streaming.
Logic thật sẽ nằm ở scripts/producer.py (Week 3) và 1 consumer service riêng.
Xem docs/decisions/003-micro-batch-not-streaming-insert.md.
"""
