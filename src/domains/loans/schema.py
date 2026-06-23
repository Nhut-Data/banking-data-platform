from pydantic import BaseModel, field_validator


class LoanRaw(BaseModel):
    loan_id:       str
    customer_id:   str
    loan_amount:   float | None = None
    interest_rate: float | None = None
    start_date:    str | None = None

    @field_validator("loan_amount")
    @classmethod
    def amount_positive(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError(f"loan_amount phải > 0, nhận {v}")
        return v

    @field_validator("interest_rate")
    @classmethod
    def rate_range(cls, v: float | None) -> float | None:
        if v is not None and not (0 < v < 100):
            raise ValueError(f"interest_rate {v} ngoài range hợp lệ")
        return v
