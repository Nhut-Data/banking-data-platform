# src/streaming/consumer.py
"""
Consumer service — chạy như Docker service riêng, KHÔNG qua Airflow.

Flow:
    Kafka topic transactions.events
        → validate Pydantic schema
        → gom micro-batch (mỗi 30s hoặc 100 messages)
        → MERGE vào PostgreSQL raw_transactions (idempotent theo transaction_id)
        → message lỗi schema → DLQ topic
"""
import json
import time
from datetime import datetime, timezone

import pandas as pd
from confluent_kafka import Consumer, KafkaException, KafkaError
from sqlalchemy import text
from pathlib import Path

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger
from src.infrastructure.postgres_client import get_engine
from src.streaming.schemas import TransactionEvent

logger = get_logger(__name__)

BATCH_SIZE = 100        # flush khi đủ 100 messages
BATCH_TIMEOUT_SEC = 30  # hoặc flush sau 30s dù chưa đủ 100


def create_consumer() -> Consumer:
    return Consumer({
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "group.id": "banking-consumer-group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,   # manual commit sau khi ghi DB thành công
        "session.timeout.ms": 30000,
        "max.poll.interval.ms": 300000,
    })


def create_raw_transactions_table() -> None:
    """Đọc DDL từ sql/postgres/ddl/raw_transactions.sql — single source of truth."""
    # Tìm project root = thư mục chứa pyproject.toml
    current = Path(__file__).resolve()
    project_root = current
    for _ in range(10):
        if (project_root / "pyproject.toml").exists():
            break
        project_root = project_root.parent

    sql_path = project_root / "sql" / "postgres" / "ddl" / "raw_transactions.sql"
    if not sql_path.exists():
        raise FileNotFoundError(f"DDL file không tìm thấy: {sql_path}")

    ddl = sql_path.read_text()
    with get_engine().connect() as conn:
        for statement in ddl.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    logger.info("Table raw_transactions ready | source=%s", sql_path)

def merge_batch(batch: list[dict]) -> int:
    """
    MERGE batch vào PostgreSQL — idempotent theo transaction_id.
    Duplicate transaction_id → UPDATE (không insert lại).
    Return số rows actually inserted.
    """
    if not batch:
        return 0

    df = pd.DataFrame(batch)

    merge_sql = text("""
        INSERT INTO raw_transactions (
            transaction_id, account_id, merchant_id,
            amount_usd, transaction_date, ingested_at,
            kafka_partition, kafka_offset
        )
        VALUES (
            :transaction_id, :account_id, :merchant_id,
            :amount_usd, :transaction_date, :ingested_at,
            :kafka_partition, :kafka_offset
        )
        ON CONFLICT (transaction_id) DO UPDATE SET
            ingested_at     = EXCLUDED.ingested_at,
            kafka_partition = EXCLUDED.kafka_partition,
            kafka_offset    = EXCLUDED.kafka_offset
    """)

    with get_engine().connect() as conn:
        conn.execute(merge_sql, df.to_dict(orient="records"))
        conn.commit()

    logger.info("Merged batch | rows=%d", len(batch))
    return len(batch)


def send_to_dlq_raw(raw_value: bytes, error: str) -> None:
    """Message không parse được → ghi vào DLQ topic."""
    from confluent_kafka import Producer
    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
    try:
        producer.produce(
            topic=settings.kafka_topic_dlq,
            value=json.dumps({
                "raw_value": raw_value.decode("utf-8", errors="replace"),
                "error": error,
                "failed_at": datetime.now(timezone.utc).isoformat(),
            }).encode("utf-8"),
        )
        producer.flush(timeout=5)
        logger.error("DLQ | error=%s", error)
    except KafkaException as e:
        logger.critical("DLQ send FAILED | error=%s", e)


def run_consumer() -> None:
    logger.info("Consumer starting | batch_size=%d | timeout=%ds",
                BATCH_SIZE, BATCH_TIMEOUT_SEC)

    create_raw_transactions_table()

    consumer = create_consumer()
    consumer.subscribe([settings.kafka_topic_transactions])

    batch: list[dict] = []
    last_flush = time.time()
    total_processed = 0

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            # flush khi đủ batch size hoặc timeout
            should_flush = (
                len(batch) >= BATCH_SIZE or
                (time.time() - last_flush) >= BATCH_TIMEOUT_SEC
            )

            if should_flush and batch:
                count = merge_batch(batch)
                total_processed += count
                consumer.commit()
                logger.info(
                    "Flushed | batch=%d | total=%d",
                    len(batch), total_processed
                )
                batch = []
                last_flush = time.time()

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error("Consumer error | %s", msg.error())
                continue

            # validate message
            try:
                event = TransactionEvent.from_json(msg.value().decode("utf-8"))
                batch.append({
                    "transaction_id":   event.transaction_id,
                    "account_id":       event.account_id,
                    "merchant_id":      event.merchant_id,
                    "amount_usd":       event.amount_usd,
                    "transaction_date": event.transaction_date,
                    "ingested_at":      datetime.now(timezone.utc),
                    "kafka_partition":  msg.partition(),
                    "kafka_offset":     msg.offset(),
                })
            except Exception as e:
                send_to_dlq_raw(msg.value(), str(e))

    except KeyboardInterrupt:
        logger.info("Consumer stopped | total_processed=%d", total_processed)
    finally:
        if batch:
            merge_batch(batch)
            consumer.commit()
        consumer.close()


if __name__ == "__main__":
    run_consumer()