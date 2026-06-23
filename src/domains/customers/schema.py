from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class CustomerRaw(BaseModel):
    customer_id:  str
    first_name:   str
    last_name:    str
    email:        str
    city:         str | None = None
    credit_score: int | None = None
    created_at:   str | None = None

    @field_validator("customer_id")
    @classmethod
    def customer_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("customer_id không được rỗng")
        return v.strip()

    @field_validator("credit_score")
    @classmethod
    def credit_score_range(cls, v: int | None) -> int | None:
        if v is not None and not (300 <= v <= 850):
            raise ValueError(f"credit_score {v} ngoài range 300-850")
        return v