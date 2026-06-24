import json
import random
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from faker import Faker
from confluent_kafka import Producer, KafkaException

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger
from src.streaming.schemas import TransactionEvent

logger = get_logger(__name__)
fake = Faker()


def load_reference_ids() -> tuple[list[str], list[str]]:
    db_path = Path(settings.sqlite_db_path)
    with sqlite3.connect(db_path) as conn:
        account_ids = [
            row[0] for row in
            conn.execute("SELECT account_id FROM accounts").fetchall()
        ]
        merchant_ids = [
            row[0] for row in
            conn.execute("SELECT merchant_id FROM merchants").fetchall()
        ]
    logger.info(
        "Loaded reference IDs | accounts=%d | merchants=%d",
        len(account_ids), len(merchant_ids)
    )
    return account_ids, merchant_ids


def generate_transaction(
    account_ids: list[str],
    merchant_ids: list[str],
) -> TransactionEvent:
    return TransactionEvent(
        transaction_id=f"TXN{uuid4().hex[:12].upper()}",
        account_id=random.choice(account_ids),
        merchant_id=random.choice(merchant_ids),
        amount_usd=round(random.uniform(1.0, 15000.0), 2),
        transaction_date=datetime.now(timezone.utc),
    )


def create_producer() -> Producer:
    return Producer({
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "acks": "all",
        "retries": 3,
        "retry.backoff.ms": 500,
        "request.timeout.ms": 30000,
        "socket.timeout.ms": 10000,
    })


def delivery_report(err, msg) -> None:
    """Callback khi message được deliver hoặc fail."""
    if err:
        logger.error("Delivery FAILED | error=%s", err)
    else:
        logger.debug(
            "Delivered | topic=%s | partition=%d | offset=%d",
            msg.topic(), msg.partition(), msg.offset()
        )


def publish_with_retry(
    producer: Producer,
    event: TransactionEvent,
    max_retries: int = 3,
) -> bool:
    delay = 1.0
    for attempt in range(1, max_retries + 1):
        delivery_result: list[bool | None] = [None]

        def on_delivery(err, msg, result=delivery_result):
            if err:
                result[0] = False
                logger.error("Delivery FAILED | error=%s", err)
            else:
                result[0] = True

        try:
            producer.produce(
                topic=settings.kafka_topic_transactions,
                value=event.to_json().encode("utf-8"),
                key=event.transaction_id.encode("utf-8"),
                on_delivery=on_delivery,
            )
            producer.flush(timeout=10)

            if delivery_result[0] is True:
                return True
            raise KafkaException("Delivery failed or timed out")

        except (KafkaException, BufferError) as e:
            logger.warning(
                "Publish failed | attempt=%d/%d | id=%s | error=%s",
                attempt, max_retries, event.transaction_id, e
            )
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
    return False



def send_to_dlq(producer: Producer, event: TransactionEvent) -> None:
    try:
        producer.produce(
            topic=settings.kafka_topic_dlq,
            value=json.dumps({
                "failed_event": event.to_json(),
                "failed_at": datetime.now(timezone.utc).isoformat(),
                "reason": "max_retries_exceeded",
            }).encode("utf-8"),
        )
        producer.flush()
        logger.error("Sent to DLQ | transaction_id=%s", event.transaction_id)
    except KafkaException as e:
        logger.critical("DLQ send FAILED | error=%s", e)


def run_producer(interval_seconds: float = 2.0) -> None:
    logger.info("Producer starting | interval=%.1fs", interval_seconds)
    account_ids, merchant_ids = load_reference_ids()
    producer = create_producer()

    published = 0
    failed = 0

    try:
        while True:
            event = generate_transaction(account_ids, merchant_ids)
            success = publish_with_retry(producer, event)

            if success:
                published += 1
                logger.info(
                    "Published | id=%s | account=%s | amount=%.2f | total=%d",
                    event.transaction_id,
                    event.account_id,
                    event.amount_usd,
                    published,
                )
            else:
                failed += 1
                send_to_dlq(producer, event)

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        logger.info(
            "Producer stopped | published=%d | failed=%d",
            published, failed
        )
    finally:
        try:
            producer.flush(timeout=5)
        except (KeyboardInterrupt, RuntimeError):
            pass

if __name__ == "__main__":
    run_producer(interval_seconds=2.0)