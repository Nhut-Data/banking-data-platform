from google.cloud import bigquery
import pandas as pd

from src.infrastructure.bigquery_client import get_full_table_id
from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def load_loans(df: pd.DataFrame, client: bigquery.Client) -> None:
    table_id = get_full_table_id(settings.bq_dataset_raw, "loans")
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=False,
        schema=[
            bigquery.SchemaField("loan_id",       "STRING",  mode="REQUIRED"),
            bigquery.SchemaField("customer_id",   "STRING",  mode="REQUIRED"),
            bigquery.SchemaField("loan_amount",   "FLOAT64"),
            bigquery.SchemaField("interest_rate", "FLOAT64"),
            bigquery.SchemaField("start_date",    "STRING"),
            bigquery.SchemaField("_ingested_at",  "TIMESTAMP", mode="REQUIRED"),
        ],
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    logger.info("Loaded loans → BigQuery | rows=%d", len(df))
