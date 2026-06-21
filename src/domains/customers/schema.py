"""
Schema/contract cho domain customers.
Dùng Pydantic để validate data trước khi load vào BigQuery.
"""
from pydantic import BaseModel


class CustomersSchema(BaseModel):
    # TODO: định nghĩa field theo đúng cột thật trong customers.csv
    pass
