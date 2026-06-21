"""
Transform layer cho domain loans.
Business logic / cleaning / dedup nhẹ bằng Pandas trước khi load.
Transform nặng hơn (join, aggregate) để ở sql/staging và sql/warehouse,
chạy bằng SQL trực tiếp trong BigQuery (xem docs/decisions/001-no-dbt.md).
"""
import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: implement
    raise NotImplementedError
