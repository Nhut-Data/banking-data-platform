"""
Data quality checks dùng chung cho tất cả domain.
Chạy sau transform, trước load — fail sớm, không load data bẩn lên BigQuery.
"""
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


@dataclass
class QualityResult:
    domain: str
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.errors.append(msg)
        self.passed = False

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            f"[{status}] {self.domain} | "
            f"errors={len(self.errors)} warnings={len(self.warnings)}"
        )


def check_nulls(
    result: QualityResult,
    df: pd.DataFrame,
    required_cols: list[str],
) -> None:
    for col in required_cols:
        null_count = df[col].isna().sum()
        if null_count > 0:
            result.fail(f"NULL check FAILED | col={col} | null_count={null_count}")
        else:
            logger.info("NULL check OK | domain=%s | col=%s", result.domain, col)


def check_duplicates(
    result: QualityResult,
    df: pd.DataFrame,
    pk_col: str,
) -> None:
    dup_count = df[pk_col].duplicated().sum()
    if dup_count > 0:
        result.fail(f"DUPLICATE check FAILED | pk={pk_col} | dup_count={dup_count}")
    else:
        logger.info("DUPLICATE check OK | domain=%s | pk=%s", result.domain, pk_col)


def check_range(
    result: QualityResult,
    df: pd.DataFrame,
    col: str,
    min_val: float | None = None,
    max_val: float | None = None,
) -> None:
    if min_val is not None:
        violations = (df[col] < min_val).sum()
        if violations > 0:
            result.fail(
                f"RANGE check FAILED | col={col} | "
                f"value < {min_val} | count={violations}"
            )
    if max_val is not None:
        violations = (df[col] > max_val).sum()
        if violations > 0:
            result.fail(
                f"RANGE check FAILED | col={col} | "
                f"value > {max_val} | count={violations}"
            )
    if result.passed:
        logger.info("RANGE check OK | domain=%s | col=%s", result.domain, col)


def check_row_count(
    result: QualityResult,
    df: pd.DataFrame,
    min_rows: int = 1,
) -> None:
    if len(df) < min_rows:
        result.fail(
            f"ROW COUNT check FAILED | "
            f"expected >= {min_rows} | got {len(df)}"
        )
    else:
        logger.info(
            "ROW COUNT check OK | domain=%s | rows=%d", result.domain, len(df)
        )


def run_quality_checks(domain: str, parquet_path: str) -> QualityResult:
    from src.domains.configs import DOMAIN_CONFIGS
    df = pd.read_parquet(parquet_path)
    result = QualityResult(domain=domain)

    if domain not in DOMAIN_CONFIGS:
        raise ValueError(f"Không có config cho domain: {domain}")

    config = DOMAIN_CONFIGS[domain]

    check_row_count(result, df, min_rows=1)
    check_nulls(result, df, required_cols=config.required_cols)
    check_duplicates(result, df, pk_col=config.pk_col)

    if config.range_checks:
        for col, (min_val, max_val) in config.range_checks.items():
            if col in df.columns:
                check_range(result, df, col=col, min_val=min_val, max_val=max_val)

    logger.info(result.summary())
    for err in result.errors:
        logger.error("  ✗ %s", err)
    for warn in result.warnings:
        logger.warning("  ⚠ %s", warn)

    return result


# ── Per-domain check functions ─────────────────────────────────

def _check_customers(result: QualityResult, df: pd.DataFrame) -> None:
    check_row_count(result, df, min_rows=1000)
    check_nulls(result, df, required_cols=["customer_id", "first_name", "last_name"])
    check_duplicates(result, df, pk_col="customer_id")
    check_range(result, df, col="credit_score", min_val=300, max_val=850)


def _check_accounts(result: QualityResult, df: pd.DataFrame) -> None:
    check_row_count(result, df, min_rows=1000)
    check_nulls(result, df, required_cols=["account_id", "customer_id"])
    check_duplicates(result, df, pk_col="account_id")
    check_range(result, df, col="balance_usd", min_val=0)


def _check_cards(result: QualityResult, df: pd.DataFrame) -> None:
    check_row_count(result, df, min_rows=1000)
    check_nulls(result, df, required_cols=["card_id", "account_id"])
    check_duplicates(result, df, pk_col="card_id")


def _check_loans(result: QualityResult, df: pd.DataFrame) -> None:
    check_row_count(result, df, min_rows=100)
    check_nulls(result, df, required_cols=["loan_id", "customer_id"])
    check_duplicates(result, df, pk_col="loan_id")
    check_range(result, df, col="loan_amount", min_val=0)
    check_range(result, df, col="interest_rate", min_val=0, max_val=100)


def _check_merchants(result: QualityResult, df: pd.DataFrame) -> None:
    check_row_count(result, df, min_rows=100)
    check_nulls(result, df, required_cols=["merchant_id"])
    check_duplicates(result, df, pk_col="merchant_id")


def _check_branches(result: QualityResult, df: pd.DataFrame) -> None:
    check_row_count(result, df, min_rows=10)
    check_nulls(result, df, required_cols=["branch_id"])
    check_duplicates(result, df, pk_col="branch_id")