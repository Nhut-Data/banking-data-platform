"""
Schema/contract cho domain merchants.
Dùng Pydantic để validate data trước khi load vào BigQuery.
"""
from pydantic import BaseModel


class MerchantsSchema(BaseModel):
    # TODO: định nghĩa field theo đúng cột thật trong merchants.csv
    pass
