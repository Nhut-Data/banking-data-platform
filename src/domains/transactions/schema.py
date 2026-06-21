"""
Schema cho 1 transaction event - dùng để validate message đọc từ Kafka
trước khi load vào BigQuery. Message không hợp lệ -> đẩy vào DLQ topic.
"""
from pydantic import BaseModel


class TransactionEventSchema(BaseModel):
    transaction_id: str
    # TODO: thêm field theo đúng cột thật trong table transactions (SQLite)
