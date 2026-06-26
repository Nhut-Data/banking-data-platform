from pydantic import BaseModel
from datetime import datetime


class TransactionSummaryResponse(BaseModel):
    transaction_date:   str
    total_transactions: int
    total_amount_usd:   float
    avg_amount_usd:     float


class TransactionResponse(BaseModel):
    transaction_id:   str
    account_id:       str
    merchant_id:      str
    customer_id:      str | None
    amount_usd:       float
    transaction_date: datetime