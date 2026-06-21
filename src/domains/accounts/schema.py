"""
Schema/contract cho domain accounts.
Dùng Pydantic để validate data trước khi load vào BigQuery.
"""
from pydantic import BaseModel


class AccountsSchema(BaseModel):
    # TODO: định nghĩa field theo đúng cột thật trong accounts.csv
    pass
