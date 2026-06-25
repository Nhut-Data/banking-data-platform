"""
Generic batch pipeline — dùng chung cho tất cả 6 domain tĩnh.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Type

import pandas as pd
from google.cloud import bigquery
from pydantic import BaseModel

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DomainConfig:
    table_name:    str
    pk_col:        str
    required_cols: list[str]
    schema_class:  Type[BaseModel]
    bq_schema:     list[bigquery.SchemaField]
    range_checks:  dict[str, tuple[float | None, float | None]] | None = None


def extract_from_sqlite(table_name: str) -> pd.DataFrame:
    import sqlite3
    with sqlite3.connect(Path(settings.sqlite_db_path)) as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    logger.info("Extracted | table=%s | rows=%d", table_name, len(df))
    return df


def validate_and_transform(
    df: pd.DataFrame,
    config: DomainConfig,
) -> pd.DataFrame:
    df = df.where(pd.notna(df), None)

    valid_rows, error_count = [], 0
    for row in df.to_dict(orient="records"):
        try:
            config.schema_class(**row)
            valid_rows.append(row)
        except Exception as e:
            error_count += 1
            logger.warning(
                "Invalid row | table=%s | pk=%s | error=%s",
                config.table_name, row.get(config.pk_col), e
            )

    if error_count:
        logger.warning(
            "Dropped %d/%d invalid rows | table=%s",
            error_count, len(df), config.table_name
        )

    result = pd.DataFrame(valid_rows)
    result["_ingested_at"] = datetime.now(timezone.utc)
    logger.info(
        "Transformed | table=%s | valid_rows=%d",
        config.table_name, len(result)
    )
    return result


def load_to_bigquery(
    df: pd.DataFrame,
    config: DomainConfig,
    client: bigquery.Client,
) -> None:
    table_id = (
        f"{settings.gcp_project_id}"
        f".{settings.bq_dataset_raw}"
        f".{config.table_name}"
    )
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=False,
        schema=config.bq_schema,
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    logger.info(
        "Loaded → BigQuery | table=%s | rows=%d",
        table_id, len(df)
    )
