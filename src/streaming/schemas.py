"""
Schema cho transaction event — dùng chung cho producer và consumer.
Producer serialize → JSON → Kafka → Consumer deserialize + validate.
"""
from datetime import datetime

from pydantic import BaseModel, field_validator


class TransactionEvent(BaseModel):
    transaction_id:   str
    account_id:       str
    merchant_id:      str
    amount_usd:       float
    transaction_date: datetime

    @field_validator("transaction_id")
    @classmethod
    def id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("transaction_id không được rỗng")
        return v.strip()

    @field_validator("amount_usd")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"amount_usd phải > 0, nhận {v}")
        return round(v, 2)

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "TransactionEvent":
        return cls.model_validate_json(data)