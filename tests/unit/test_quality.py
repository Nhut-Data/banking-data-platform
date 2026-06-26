"""Unit tests cho data quality checks."""
import pandas as pd
import pytest
import tempfile
import os

from src.infrastructure.quality import (
    QualityResult, check_nulls, check_duplicates,
    check_range, check_row_count, run_quality_checks,
)


def make_parquet(data: list[dict]) -> str:
    """Helper: tạo temp parquet file từ list of dicts."""
    df = pd.DataFrame(data)
    tmp = tempfile.NamedTemporaryFile(suffix=".parquet", delete=False)
    df.to_parquet(tmp.name, index=False)
    return tmp.name


class TestQualityResult:
    def test_initial_state(self):
        r = QualityResult(domain="test")
        assert r.passed is True
        assert r.errors == []

    def test_fail_sets_passed_false(self):
        r = QualityResult(domain="test")
        r.fail("something wrong")
        assert r.passed is False
        assert len(r.errors) == 1


class TestCheckNulls:
    def test_no_nulls_pass(self):
        r = QualityResult(domain="test")
        df = pd.DataFrame({"id": ["A", "B"], "name": ["X", "Y"]})
        check_nulls(r, df, required_cols=["id", "name"])
        assert r.passed is True

    def test_null_fails(self):
        r = QualityResult(domain="test")
        df = pd.DataFrame({"id": ["A", None]})
        check_nulls(r, df, required_cols=["id"])
        assert r.passed is False


class TestCheckDuplicates:
    def test_no_duplicates_pass(self):
        r = QualityResult(domain="test")
        df = pd.DataFrame({"id": ["A", "B", "C"]})
        check_duplicates(r, df, pk_col="id")
        assert r.passed is True

    def test_duplicates_fail(self):
        r = QualityResult(domain="test")
        df = pd.DataFrame({"id": ["A", "A", "B"]})
        check_duplicates(r, df, pk_col="id")
        assert r.passed is False


class TestCheckRange:
    def test_in_range_pass(self):
        r = QualityResult(domain="test")
        df = pd.DataFrame({"score": [300, 500, 850]})
        check_range(r, df, col="score", min_val=300, max_val=850)
        assert r.passed is True

    def test_below_min_fail(self):
        r = QualityResult(domain="test")
        df = pd.DataFrame({"score": [299, 500]})
        check_range(r, df, col="score", min_val=300)
        assert r.passed is False

    def test_above_max_fail(self):
        r = QualityResult(domain="test")
        df = pd.DataFrame({"score": [500, 851]})
        check_range(r, df, col="score", max_val=850)
        assert r.passed is False


class TestCheckRowCount:
    def test_sufficient_rows_pass(self):
        r = QualityResult(domain="test")
        df = pd.DataFrame({"id": range(100)})
        check_row_count(r, df, min_rows=50)
        assert r.passed is True

    def test_insufficient_rows_fail(self):
        r = QualityResult(domain="test")
        df = pd.DataFrame({"id": range(10)})
        check_row_count(r, df, min_rows=100)
        assert r.passed is False


class TestRunQualityChecks:
    def test_customers_pass(self):
        path = make_parquet([{
            "customer_id": f"CUS{i:03d}",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@test.com",
            "city": "Hanoi",
            "credit_score": 700,
            "created_at": "2024-01-01",
            "_ingested_at": "2024-01-01 00:00:00",
        } for i in range(100)])

        try:
            result = run_quality_checks("customers", path)
            assert result.passed is True
        finally:
            os.unlink(path)

    def test_unknown_domain_raises(self):
        with pytest.raises(ValueError):
            run_quality_checks("unknown_domain", "fake_path.parquet")