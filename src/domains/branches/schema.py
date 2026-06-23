from pydantic import BaseModel


class BranchRaw(BaseModel):
    branch_id:    str
    branch_name:  str | None = None
    manager_name: str | None = None
    city:         str | None = None   # NULL trong SQLite, giữ lại
    country:      str | None = None   # NULL trong SQLite, giữ lại
