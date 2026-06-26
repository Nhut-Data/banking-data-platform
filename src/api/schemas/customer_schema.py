from pydantic import BaseModel


class CustomerResponse(BaseModel):
    customer_id:        str
    full_name:          str
    email:              str | None
    city:               str | None
    credit_score:       int | None
    credit_score_band:  str | None
    created_at:         str | None