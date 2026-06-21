"""
Schema/contract cho domain branches.
Dùng Pydantic để validate data trước khi load vào BigQuery.
"""
from pydantic import BaseModel


class BranchesSchema(BaseModel):
    # TODO: định nghĩa field theo đúng cột thật trong branches.csv
    pass
