"""
Repository pattern cho domain loans.
Tách data access khỏi business logic - đổi nguồn data sau này
(vd BigQuery -> nguồn khác) không phải sửa service/API layer.
"""
from google.cloud import bigquery


class LoansRepository:
    def __init__(self, client: bigquery.Client):
        self.client = client

    def get_by_id(self, id: str):
        # TODO: implement
        raise NotImplementedError
