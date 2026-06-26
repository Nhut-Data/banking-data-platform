"""Dependency injection cho FastAPI."""
from functools import lru_cache
from google.cloud import bigquery
from src.infrastructure.bigquery_client import get_bigquery_client
from src.infrastructure.config import settings


@lru_cache(maxsize=1)
def get_bq_client() -> bigquery.Client:
    return get_bigquery_client()


def get_project_id() -> str:
    return settings.gcp_project_id