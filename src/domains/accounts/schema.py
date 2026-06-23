from pydantic import BaseModel


class AccountRaw(BaseModel):
    account_id:   str
    customer_id:  str
    account_type: str | None = None
    balance_usd:  float | None = None
    open_date:    str | None = None