"""
Config cho 6 domain tĩnh — single source of truth.
"""
from google.cloud import bigquery
from pydantic import BaseModel, field_validator

from src.infrastructure.pipeline import DomainConfig


class CustomerSchema(BaseModel):
    customer_id:  str
    first_name:   str
    last_name:    str
    email:        str | None = None
    city:         str | None = None
    credit_score: int | None = None
    created_at:   str | None = None

    @field_validator("customer_id")
    @classmethod
    def pk_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("customer_id không được rỗng")
        return v

    @field_validator("credit_score")
    @classmethod
    def credit_score_range(cls, v):
        if v is not None and not (300 <= v <= 850):
            raise ValueError(f"credit_score {v} ngoài range 300-850")
        return v



class AccountSchema(BaseModel):
    account_id:   str
    customer_id:  str
    account_type: str | None = None
    balance_usd:  float | None = None
    open_date:    str | None = None

    @field_validator("balance_usd")
    @classmethod
    def balance_not_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError(f"balance_usd không được âm: {v}")
        return v


class CardSchema(BaseModel):
    card_id:         str
    account_id:      str
    card_type:       str | None = None
    expiration_date: str | None = None


class LoanSchema(BaseModel):
    loan_id:       str
    customer_id:   str
    loan_amount:   float | None = None
    interest_rate: float | None = None
    start_date:    str | None = None

    @field_validator("loan_amount")
    @classmethod
    def amount_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("loan_amount phải > 0")
        return v


class MerchantSchema(BaseModel):
    merchant_id:   str
    merchant_name: str | None = None
    city:          str | None = None


class BranchSchema(BaseModel):
    branch_id:    str
    branch_name:  str | None = None
    manager_name: str | None = None
    city:         str | None = None
    country:      str | None = None


S = bigquery.SchemaField

DOMAIN_CONFIGS: dict[str, DomainConfig] = {
    "customers": DomainConfig(
        table_name="customers",
        pk_col="customer_id",
        required_cols=["customer_id", "first_name", "last_name"],
        schema_class=CustomerSchema,
        range_checks={"credit_score": (300, 850)},
        bq_schema=[
            S("customer_id",  "STRING",    mode="REQUIRED"),
            S("first_name",   "STRING"),
            S("last_name",    "STRING"),
            S("email",        "STRING"),
            S("city",         "STRING"),
            S("credit_score", "INTEGER"),
            S("created_at",   "STRING"),
            S("_ingested_at", "TIMESTAMP", mode="REQUIRED"),
        ],
    ),
    "accounts": DomainConfig(
        table_name="accounts",
        pk_col="account_id",
        required_cols=["account_id", "customer_id"],
        schema_class=AccountSchema,
        range_checks={"balance_usd": (0, None)},
        bq_schema=[
            S("account_id",   "STRING",  mode="REQUIRED"),
            S("customer_id",  "STRING",  mode="REQUIRED"),
            S("account_type", "STRING"),
            S("balance_usd",  "FLOAT64"),
            S("open_date",    "STRING"),
            S("_ingested_at", "TIMESTAMP", mode="REQUIRED"),
        ],
    ),
    "cards": DomainConfig(
        table_name="cards",
        pk_col="card_id",
        required_cols=["card_id", "account_id"],
        schema_class=CardSchema,
        bq_schema=[
            S("card_id",         "STRING", mode="REQUIRED"),
            S("account_id",      "STRING", mode="REQUIRED"),
            S("card_type",       "STRING"),
            S("expiration_date", "STRING"),
            S("_ingested_at",    "TIMESTAMP", mode="REQUIRED"),
        ],
    ),
    "loans": DomainConfig(
        table_name="loans",
        pk_col="loan_id",
        required_cols=["loan_id", "customer_id"],
        schema_class=LoanSchema,
        range_checks={"loan_amount": (0, None), "interest_rate": (0, 100)},
        bq_schema=[
            S("loan_id",       "STRING",  mode="REQUIRED"),
            S("customer_id",   "STRING",  mode="REQUIRED"),
            S("loan_amount",   "FLOAT64"),
            S("interest_rate", "FLOAT64"),
            S("start_date",    "STRING"),
            S("_ingested_at",  "TIMESTAMP", mode="REQUIRED"),
        ],
    ),
    "merchants": DomainConfig(
        table_name="merchants",
        pk_col="merchant_id",
        required_cols=["merchant_id"],
        schema_class=MerchantSchema,
        bq_schema=[
            S("merchant_id",   "STRING", mode="REQUIRED"),
            S("merchant_name", "STRING"),
            S("city",          "STRING"),
            S("_ingested_at",  "TIMESTAMP", mode="REQUIRED"),
        ],
    ),
    "branches": DomainConfig(
        table_name="branches",
        pk_col="branch_id",
        required_cols=["branch_id"],
        schema_class=BranchSchema,
        bq_schema=[
            S("branch_id",    "STRING", mode="REQUIRED"),
            S("branch_name",  "STRING"),
            S("manager_name", "STRING"),
            S("city",         "STRING"),
            S("country",      "STRING"),
            S("_ingested_at", "TIMESTAMP", mode="REQUIRED"),
        ],
    ),
}
