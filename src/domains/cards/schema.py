"""
Schema/contract cho domain cards.
Dùng Pydantic để validate data trước khi load vào BigQuery.
"""
from pydantic import BaseModel


class CardsSchema(BaseModel):
    # TODO: định nghĩa field theo đúng cột thật trong cards.csv
    pass
