from pydantic import BaseModel


class MerchantRaw(BaseModel):
    merchant_id:   str
    merchant_name: str | None = None
    city:          str | None = None
