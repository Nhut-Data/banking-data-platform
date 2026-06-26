from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import bigquery

from src.api.dependencies import get_bq_client, get_project_id
from src.api.schemas.customer_schema import CustomerResponse

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: str,
    client: bigquery.Client = Depends(get_bq_client),
    project_id: str = Depends(get_project_id),
) -> CustomerResponse:
    query = f"""
        SELECT
            customer_id, full_name, email, city,
            credit_score, credit_score_band,
            CAST(created_at AS STRING) AS created_at
        FROM `{project_id}.warehouse.dim_customer`
        WHERE customer_id = @customer_id
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id)
        ]
    )
    rows = list(client.query(query, job_config=job_config).result())
    if not rows:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    row = dict(rows[0])
    return CustomerResponse(**row)


@router.get("/", response_model=list[CustomerResponse])
def list_customers(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    city: str | None = Query(default=None),
    credit_score_band: str | None = Query(default=None),
    client: bigquery.Client = Depends(get_bq_client),
    project_id: str = Depends(get_project_id),
) -> list[CustomerResponse]:
    filters = []
    params = []

    if city:
        filters.append("city = @city")
        params.append(bigquery.ScalarQueryParameter("city", "STRING", city))
    if credit_score_band:
        filters.append("credit_score_band = @band")
        params.append(bigquery.ScalarQueryParameter("band", "STRING", credit_score_band))

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    query = f"""
        SELECT
            customer_id, full_name, email, city,
            credit_score, credit_score_band,
            CAST(created_at AS STRING) AS created_at
        FROM `{project_id}.warehouse.dim_customer`
        {where_clause}
        ORDER BY customer_id
        LIMIT @limit OFFSET @offset
    """
    params += [
        bigquery.ScalarQueryParameter("limit", "INT64", limit),
        bigquery.ScalarQueryParameter("offset", "INT64", offset),
    ]
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    rows = list(client.query(query, job_config=job_config).result())
    return [CustomerResponse(**dict(r)) for r in rows]