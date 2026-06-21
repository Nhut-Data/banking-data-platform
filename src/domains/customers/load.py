"""
Load layer cho domain customers.
Đẩy DataFrame đã transform vào BigQuery raw.customers.
"""
import pandas as pd
from google.cloud import bigquery


def load(df: pd.DataFrame, client: bigquery.Client, table_id: str) -> None:
    # TODO: implement, dùng client.load_table_from_dataframe
    raise NotImplementedError
