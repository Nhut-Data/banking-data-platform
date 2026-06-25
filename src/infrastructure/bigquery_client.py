"""
BigQuery client dùng Application Default Credentials (ADC).
Local: credentials từ gcloud auth application-default login
Docker: mount ~/.config/gcloud vào container
"""
from google.cloud import bigquery

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def get_bigquery_client() -> bigquery.Client:
    client = bigquery.Client(
        project=settings.gcp_project_id,
        location=settings.bq_location,
    )
    logger.info("BigQuery client initialized | project=%s", settings.gcp_project_id)
    return client


def get_full_table_id(dataset: str, table: str) -> str:
    return f"{settings.gcp_project_id}.{dataset}.{table}"
