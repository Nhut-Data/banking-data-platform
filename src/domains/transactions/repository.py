"""
Repository pattern cho domain transactions.
"""
from google.cloud import bigquery


class TransactionsRepository:
    def __init__(self, client: bigquery.Client):
        self.client = client

    def get_by_id(self, transaction_id: str):
        # TODO: implement
        raise NotImplementedError
