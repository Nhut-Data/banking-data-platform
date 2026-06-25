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
            from src.infrastructure.pipeline import extract_from_sqlite
            df = extract_from_sqlite(domain_name)
            path = f"/opt/airflow/data/parquet_staging/{domain_name}.parquet"
            df.to_parquet(path, index=False)
            return path

        @task(task_id=f"transform_{domain}")
        def transform(parquet_path: str, domain_name: str = domain) -> str:
            import pandas as pd
            from src.infrastructure.pipeline import validate_and_transform
            from src.domains.configs import DOMAIN_CONFIGS
            df = pd.read_parquet(parquet_path)
            config = DOMAIN_CONFIGS[domain_name]
            df_clean = validate_and_transform(df, config)
            out_path = parquet_path.replace(".parquet", "_clean.parquet")
            df_clean.to_parquet(out_path, index=False)
            return out_path

        @task(task_id=f"load_{domain}")
        def load(parquet_path: str, domain_name: str = domain) -> None:
            import pandas as pd
            from src.infrastructure.pipeline import load_to_bigquery
            from src.infrastructure.bigquery_client import get_bigquery_client
            from src.domains.configs import DOMAIN_CONFIGS
            df = pd.read_parquet(parquet_path)
            config = DOMAIN_CONFIGS[domain_name]
            client = get_bigquery_client()
            load_to_bigquery(df, config, client)

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