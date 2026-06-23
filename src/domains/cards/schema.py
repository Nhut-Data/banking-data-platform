from pydantic import BaseModel


class CardRaw(BaseModel):
    card_id:         str
    account_id:      str
    card_type:       str | None = None
    expiration_date: str | None = None
