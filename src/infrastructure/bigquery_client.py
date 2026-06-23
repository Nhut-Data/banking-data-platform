from google.cloud import bigquery
from google.oauth2 import service_account

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def get_bigquery_client() -> bigquery.Client:
    credentials = service_account.Credentials.from_service_account_file(
        settings.google_application_credentials,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(
        project=settings.gcp_project_id,
        credentials=credentials,
        location=settings.bq_location,
    )
    logger.info("BigQuery client initialized | project=%s", settings.gcp_project_id)
    return client


def get_full_table_id(dataset: str, table: str) -> str:
    """Trả về fully-qualified table ID: project.dataset.table"""
    return f"{settings.gcp_project_id}.{dataset}.{table}"