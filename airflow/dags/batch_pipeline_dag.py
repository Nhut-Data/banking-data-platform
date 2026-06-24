"""
Batch pipeline DAG — extract 6 entity tĩnh từ SQLite → BigQuery raw.
Schedule: @daily (chạy mỗi ngày 1 lần, hoặc trigger thủ công khi cần reload)

Luồng:
    [extract_<domain>] → [transform_<domain>] → [load_<domain>]
                                                        ↓ (tất cả load xong)
                                               [data_quality_check]
                                                        ↓
                                              [trigger_sql_transforms]
"""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
import pandas as pd
import importlib

DEFAULT_ARGS = {
    "owner": "nhut",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
}

DOMAINS = ["customers", "accounts", "cards", "loans", "merchants", "branches"]


@dag(
    dag_id="batch_pipeline",
    description="Extract 6 entity tĩnh từ SQLite → BigQuery raw",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["batch", "sqlite", "bigquery"],
)
def batch_pipeline():

    start = EmptyOperator(task_id="start")
    quality_check = EmptyOperator(task_id="data_quality_check")   # Day 10
    sql_transforms = EmptyOperator(task_id="trigger_sql_transforms")  # Day 13
    end = EmptyOperator(task_id="end")

    load_tasks = []

    for domain in DOMAINS:

        @task(task_id=f"extract_{domain}")
        def extract(domain_name: str = domain) -> str:
            import importlib
            mod = importlib.import_module(f"src.domains.{domain_name}.extract")
            fn = getattr(mod, f"extract_{domain_name}")
            df = fn()
            path = f"/opt/airflow/data/parquet_staging/{domain_name}.parquet"
            df.to_parquet(path, index=False)
            return path

        @task(task_id=f"transform_{domain}")
        def transform(parquet_path: str, domain_name: str = domain) -> str:
            mod = importlib.import_module(f"src.domains.{domain_name}.transform")
            fn = getattr(mod, f"transform_{domain_name}")
            df = pd.read_parquet(parquet_path)
            df_clean = fn(df)
            out_path = parquet_path.replace(".parquet", "_clean.parquet")
            df_clean.to_parquet(out_path, index=False)
            return out_path

        @task(task_id=f"load_{domain}")
        def load(parquet_path: str, domain_name: str = domain) -> None:
            from src.infrastructure.bigquery_client import get_bigquery_client
            mod = importlib.import_module(f"src.domains.{domain_name}.load")
            fn = getattr(mod, f"load_{domain_name}")
            df = pd.read_parquet(parquet_path)
            client = get_bigquery_client()
            fn(df, client)

        extracted = extract()
        transformed = transform(extracted)
        loaded = load(transformed)

        start >> extracted
        load_tasks.append(loaded)

    load_tasks >> quality_check >> sql_transforms >> end


batch_pipeline()