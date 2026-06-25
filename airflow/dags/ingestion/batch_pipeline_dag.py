from __future__ import annotations
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from src.infrastructure.quality import run_quality_checks
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
    sql_transforms = EmptyOperator(task_id="trigger_sql_transforms")
    end = EmptyOperator(task_id="end")

    load_tasks = []

    for domain in DOMAINS:

        @task(task_id=f"extract_{domain}")
        def extract(domain_name: str = domain) -> str:
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

    @task(task_id="data_quality_check")
    def data_quality_check() -> None:
        failed_domains = []
        for domain in DOMAINS:
            path = f"/opt/airflow/data/parquet_staging/{domain}_clean.parquet"
            result = run_quality_checks(domain, path)
            if not result.passed:
                failed_domains.append(domain)
        if failed_domains:
            raise ValueError(f"Quality FAILED: {failed_domains}")

    quality_check = data_quality_check()
    load_tasks >> quality_check >> sql_transforms >> end


batch_pipeline()