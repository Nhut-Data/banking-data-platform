from fastapi import APIRouter, Depends, Query
from google.cloud import bigquery

from src.api.dependencies import get_bq_client, get_project_id
from src.api.schemas.transaction_schema import (
    TransactionSummaryResponse,
    TransactionResponse,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/daily-summary", response_model=list[TransactionSummaryResponse])
def get_daily_summary(
    days: int = Query(default=7, ge=1, le=90),
    client: bigquery.Client = Depends(get_bq_client),
    project_id: str = Depends(get_project_id),
) -> list[TransactionSummaryResponse]:
    query = f"""
        SELECT
            CAST(DATE(transaction_date) AS STRING) AS transaction_date,
            COUNT(*)                                AS total_transactions,
            ROUND(SUM(amount_usd), 2)               AS total_amount_usd,
            ROUND(AVG(amount_usd), 2)               AS avg_amount_usd
        FROM `{project_id}.warehouse.fact_transaction`
        WHERE transaction_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
        GROUP BY 1
        ORDER BY 1 DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("days", "INT64", days)]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return [TransactionSummaryResponse(**dict(r)) for r in rows]


@router.get("/by-account/{account_id}", response_model=list[TransactionResponse])
def get_transactions_by_account(
    account_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    client: bigquery.Client = Depends(get_bq_client),
    project_id: str = Depends(get_project_id),
) -> list[TransactionResponse]:
    query = f"""
        SELECT
            transaction_id, account_id, merchant_id,
            customer_id, amount_usd, transaction_date
        FROM `{project_id}.warehouse.fact_transaction`
        WHERE account_id = @account_id
        ORDER BY transaction_date DESC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("account_id", "STRING", account_id),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    rows = list(client.query(query, job_config=job_config).result())
    return [TransactionResponse(**dict(r)) for r in rows]

@router.get("/summary", response_model=list[TransactionSummaryResponse])
def get_mart_summary(
    client: bigquery.Client = Depends(get_bq_client),
    project_id: str = Depends(get_project_id),
) -> list[TransactionSummaryResponse]:
    query = f"""
        SELECT
            CAST(transaction_date AS STRING) AS transaction_date,
            total_transactions,
            total_amount_usd,
            avg_amount_usd
        FROM `{project_id}.marts.daily_transaction_summary`
        ORDER BY transaction_date DESC
        LIMIT 30
    """
    rows = list(client.query(query).result())
    return [TransactionSummaryResponse(**dict(r)) for r in rows]