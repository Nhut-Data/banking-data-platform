"""
Transform nhẹ cho transaction event (validate/clean) trước khi load.
Transform nặng hơn (build fact_transaction) nằm ở sql/warehouse/fact_transaction.sql.
"""
import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: implement
    raise NotImplementedError
