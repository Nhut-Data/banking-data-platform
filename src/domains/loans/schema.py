"""
Schema/contract cho domain loans.
Dùng Pydantic để validate data trước khi load vào BigQuery.
"""
from pydantic import BaseModel


class LoansSchema(BaseModel):
    # TODO: định nghĩa field theo đúng cột thật trong loans.csv
    pass
