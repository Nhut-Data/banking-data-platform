"""
Load micro-batch transaction events vào BigQuery raw.transactions.
Dùng MERGE theo transaction_id để đảm bảo idempotent (tránh duplicate
do Kafka at-least-once delivery).
"""
import pandas as pd
from google.cloud import bigquery


def load_merge(df: pd.DataFrame, client: bigquery.Client, table_id: str) -> None:
    # TODO: implement MERGE statement, key = transaction_id
    raise NotImplementedError
