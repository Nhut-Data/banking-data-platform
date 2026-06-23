from google.cloud import bigquery
import pandas as pd

from src.infrastructure.bigquery_client import get_full_table_id
from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def load_merchants(df: pd.DataFrame, client: bigquery.Client) -> None:
    table_id = get_full_table_id(settings.bq_dataset_raw, "merchants")
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=False,
        schema=[
            bigquery.SchemaField("merchant_id",   "STRING", mode="REQUIRED"),
            bigquery.SchemaField("merchant_name", "STRING"),
            bigquery.SchemaField("city",          "STRING"),
            bigquery.SchemaField("_ingested_at",  "TIMESTAMP", mode="REQUIRED"),
        ],
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    logger.info("Loaded merchants → BigQuery | rows=%d", len(df))
