from google.cloud import bigquery
import pandas as pd

from src.infrastructure.bigquery_client import get_full_table_id
from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)

TABLE = "customers"


def load_customers(df: pd.DataFrame, client: bigquery.Client) -> None:
    """Load DataFrame vào BigQuery raw.customers — WRITE_TRUNCATE cho batch tĩnh."""
    table_id = get_full_table_id(settings.bq_dataset_raw, TABLE)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=False,
        schema=[
            bigquery.SchemaField("customer_id",  "STRING",    mode="REQUIRED"),
            bigquery.SchemaField("first_name",   "STRING"),
            bigquery.SchemaField("last_name",    "STRING"),
            bigquery.SchemaField("email",        "STRING"),
            bigquery.SchemaField("city",         "STRING"),
            bigquery.SchemaField("credit_score", "INTEGER"),
            bigquery.SchemaField("created_at",   "STRING"),
            bigquery.SchemaField("_ingested_at", "TIMESTAMP", mode="REQUIRED"),
        ],
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # block đến khi job xong

    logger.info("Loaded customers → BigQuery | table=%s | rows=%d", table_id, len(df))