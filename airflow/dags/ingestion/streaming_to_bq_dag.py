# airflow/dags/ingestion/streaming_to_bq_dag.py
"""
Hourly DAG — đọc unprocessed transactions từ PostgreSQL buffer
→ transform → load BigQuery raw.transactions → mark processed.

Watermark pattern:
    - Đọc WHERE processed = FALSE
    - Load vào BigQuery
    - UPDATE processed = TRUE sau khi load thành công
    - Idempotent: nếu DAG fail giữa chừng → chạy lại từ đầu vẫn an toàn
"""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

DEFAULT_ARGS = {
    "owner": "nhut",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
}


@dag(
    dag_id="streaming_to_bq",
    description="Hourly: PostgreSQL raw_transactions → BigQuery",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["streaming", "postgresql", "bigquery"],
)
def streaming_to_bq():

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    @task(task_id="extract_from_postgres")
    def extract_from_postgres() -> str:
        """
        Đọc unprocessed rows từ PostgreSQL.
        Return path Parquet để pass sang task tiếp theo.
        """
        import pandas as pd
        from sqlalchemy import text
        from src.infrastructure.postgres_client import get_engine
        from src.infrastructure.logger import get_logger

        logger = get_logger(__name__)

        query = text("""
            SELECT
                transaction_id,
                account_id,
                merchant_id,
                amount_usd,
                transaction_date,
                ingested_at,
                kafka_partition,
                kafka_offset
            FROM raw_transactions
            WHERE processed = FALSE
            ORDER BY ingested_at
            LIMIT 50000
        """)

        with get_engine().connect() as conn:
            df = pd.read_sql(query, conn)

        logger.info("Extracted from PostgreSQL | rows=%d", len(df))

        if df.empty:
            logger.info("No unprocessed rows — skipping")
            return ""

        path = "/opt/airflow/data/parquet_staging/raw_transactions.parquet"
        df.to_parquet(path, index=False)
        return path

    @task(task_id="validate_transactions")
    def validate_transactions(parquet_path: str) -> str:
        """Validate schema + basic quality checks."""
        if not parquet_path:
            return ""

        import pandas as pd
        from src.infrastructure.logger import get_logger
        from src.streaming.schemas import TransactionEvent

        logger = get_logger(__name__)
        df = pd.read_parquet(parquet_path)

        valid_rows, error_count = [], 0
        for row in df.to_dict(orient="records"):
            try:
                TransactionEvent(
                    transaction_id=row["transaction_id"],
                    account_id=row["account_id"],
                    merchant_id=row["merchant_id"],
                    amount_usd=float(row["amount_usd"]),
                    transaction_date=row["transaction_date"],
                )
                valid_rows.append(row)
            except Exception as e:
                error_count += 1
                logger.warning(
                    "Invalid transaction | id=%s | error=%s",
                    row.get("transaction_id"), e
                )

        if error_count:
            logger.warning("Dropped %d invalid rows", error_count)

        result = pd.DataFrame(valid_rows)
        out_path = "/opt/airflow/data/parquet_staging/raw_transactions_clean.parquet"
        result.to_parquet(out_path, index=False)
        logger.info("Validated transactions | valid=%d", len(result))
        return out_path

    @task(task_id="load_to_bigquery")
    def load_to_bigquery(parquet_path: str) -> list[str]:
        """
        Load clean transactions vào BigQuery raw.transactions.
        Return list transaction_ids đã load thành công.
        """
        if not parquet_path:
            return []

        import pandas as pd
        from google.cloud import bigquery
        from src.infrastructure.bigquery_client import get_bigquery_client
        from src.infrastructure.config import settings
        from src.infrastructure.logger import get_logger

        logger = get_logger(__name__)
        df = pd.read_parquet(parquet_path)

        if df.empty:
            return []

        # Chỉ giữ các cột BigQuery cần
        bq_cols = [
            "transaction_id", "account_id", "merchant_id",
            "amount_usd", "transaction_date"
        ]
        df_bq = df[bq_cols].copy()
        df_bq["_ingested_at"] = df["ingested_at"]

        client = get_bigquery_client()
        table_id = (
            f"{settings.gcp_project_id}"
            f".{settings.bq_dataset_raw}"
            f".transactions"
        )

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            autodetect=False,
            schema=[
                bigquery.SchemaField("transaction_id",   "STRING",    mode="REQUIRED"),
                bigquery.SchemaField("account_id",       "STRING",    mode="REQUIRED"),
                bigquery.SchemaField("merchant_id",      "STRING",    mode="REQUIRED"),
                bigquery.SchemaField("amount_usd",       "FLOAT64"),
                bigquery.SchemaField("transaction_date", "TIMESTAMP"),
                bigquery.SchemaField("_ingested_at",     "TIMESTAMP", mode="REQUIRED"),
            ],
        )

        job = client.load_table_from_dataframe(df_bq, table_id, job_config=job_config)
        job.result()

        transaction_ids = df["transaction_id"].tolist()
        logger.info("Loaded → BigQuery | rows=%d", len(transaction_ids))
        return transaction_ids

    @task(task_id="mark_processed")
    def mark_processed(transaction_ids: list[str]) -> None:
        """
        Mark transactions đã load thành công là processed = TRUE.
        Chỉ mark SAU KHI load BigQuery thành công — đảm bảo idempotency.
        """
        if not transaction_ids:
            return

        from sqlalchemy import text
        from src.infrastructure.postgres_client import get_engine
        from src.infrastructure.logger import get_logger

        logger = get_logger(__name__)

        with get_engine().connect() as conn:
            conn.execute(
                text("""
                    UPDATE raw_transactions
                    SET processed = TRUE
                    WHERE transaction_id = ANY(:ids)
                """),
                {"ids": transaction_ids},
            )
            conn.commit()

        logger.info("Marked processed | count=%d", len(transaction_ids))

    # Wire tasks
    extracted = extract_from_postgres()
    validated = validate_transactions(extracted)
    loaded = load_to_bigquery(validated)
    marked = mark_processed(loaded)

    start >> extracted >> validated >> loaded >> marked >> end


streaming_to_bq()