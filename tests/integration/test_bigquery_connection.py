"""
Integration test: verify BigQuery client kết nối được và đủ 4 dataset.
Cần .env + secrets/gcp-sa-key.json tồn tại để chạy.
"""
from src.infrastructure.bigquery_client import get_bigquery_client
from src.infrastructure.config import settings


def test_bigquery_connection():
    client = get_bigquery_client()
    dataset_ids = {d.dataset_id for d in client.list_datasets()}

    expected = {
        settings.bq_dataset_raw,
        settings.bq_dataset_staging,
        settings.bq_dataset_warehouse,
        settings.bq_dataset_marts,
    }
    missing = expected - dataset_ids
    assert not missing, f"Thiếu dataset: {missing}"