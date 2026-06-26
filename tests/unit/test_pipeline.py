"""Unit tests cho generic pipeline layer."""
import pandas as pd
import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from src.infrastructure.pipeline import validate_and_transform, DomainConfig
from src.domains.configs import DOMAIN_CONFIGS


def make_customer(**overrides) -> dict:
    base = {
        "customer_id": "CUS001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "city": "Hanoi",
        "credit_score": 750,
        "created_at": "2024-01-01 00:00:00",
    }
    return {**base, **overrides}


def make_account(**overrides) -> dict:
    base = {
        "account_id": "ACC001",
        "customer_id": "CUS001",
        "account_type": "Savings",
        "balance_usd": 10000.0,
        "open_date": "2024-01-01",
    }
    return {**base, **overrides}


class TestValidateAndTransform:

    def test_valid_customers_pass(self):
        df = pd.DataFrame([make_customer(), make_customer(customer_id="CUS002")])
        config = DOMAIN_CONFIGS["customers"]
        result = validate_and_transform(df, config)
        assert len(result) == 2
        assert "_ingested_at" in result.columns

    def test_invalid_pk_dropped(self):
        df = pd.DataFrame([
            make_customer(customer_id="CUS001"),
            make_customer(customer_id=""),   # empty PK
        ])
        config = DOMAIN_CONFIGS["customers"]
        result = validate_and_transform(df, config)
        assert len(result) == 1

    def test_credit_score_out_of_range_dropped(self):
        df = pd.DataFrame([
            make_customer(credit_score=750),   # valid
            make_customer(credit_score=100),   # invalid: < 300
            make_customer(credit_score=900),   # invalid: > 850
        ])
        config = DOMAIN_CONFIGS["customers"]
        result = validate_and_transform(df, config)
        assert len(result) == 1

    def test_ingested_at_added(self):
        df = pd.DataFrame([make_customer()])
        config = DOMAIN_CONFIGS["customers"]
        result = validate_and_transform(df, config)
        assert "_ingested_at" in result.columns
        assert result["_ingested_at"].dtype.tz is not None  # timezone-aware

    def test_none_values_handled(self):
        """NaN → None cho Optional fields không gây lỗi."""
        import numpy as np
        df = pd.DataFrame([make_customer(city=np.nan, credit_score=np.nan)])
        config = DOMAIN_CONFIGS["customers"]
        result = validate_and_transform(df, config)
        assert len(result) == 1

    def test_account_negative_balance_dropped(self):
        df = pd.DataFrame([
            make_account(balance_usd=1000.0),    # valid
            make_account(balance_usd=-500.0),    # invalid
        ])
        config = DOMAIN_CONFIGS["accounts"]
        result = validate_and_transform(df, config)
        assert len(result) == 1

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["customer_id", "first_name", "last_name",
                                    "email", "city", "credit_score", "created_at"])
        config = DOMAIN_CONFIGS["customers"]
        result = validate_and_transform(df, config)
        assert len(result) == 0