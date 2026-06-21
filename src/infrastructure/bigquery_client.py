"""
Wrapper tạo BigQuery client dùng chung.
"""
from google.cloud import bigquery
from google.oauth2 import service_account

from src.infrastructure.config import settings


def get_bigquery_client() -> bigquery.Client:
    credentials = service_account.Credentials.from_service_account_file(
        settings.google_application_credentials
    )
    return bigquery.Client(
        project=settings.gcp_project_id,
        credentials=credentials,
        location=settings.bq_location,
    )