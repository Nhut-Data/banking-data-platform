"""
Extract layer cho domain accounts.
Nguồn: data/raw/accounts.csv (batch, static)
Output: DataFrame thô -> load.py đẩy vào BigQuery raw.accounts
"""
import pandas as pd
from pathlib import Path


def extract(csv_path: Path) -> pd.DataFrame:
    """Đọc CSV thô, KHÔNG transform logic ở đây, chỉ đọc + cast type cơ bản nếu cần."""
    # TODO: implement
    raise NotImplementedError
