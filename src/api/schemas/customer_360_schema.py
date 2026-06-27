from pydantic import BaseModel
from datetime import datetime


class Customer360Response(BaseModel):
    customer_id:         str
    full_name:           str
    email:               str | None
    city:                str | None
    credit_score:        int | None
    credit_score_band:   str | None
    total_accounts:      int
    total_balance_usd:   float | None
    total_loans:         int
    total_loan_amount:   float | None
    avg_interest_rate:   float | None
    total_cards:         int
    active_cards:        int
    total_transactions:  int
    total_spent_usd:     float | None
    avg_transaction_usd: float | None
    last_transaction_at: datetime | None
