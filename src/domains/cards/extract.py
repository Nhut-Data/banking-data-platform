"""
Extract layer cho domain cards.
Nguồn: data/raw/cards.csv (batch, static)
Output: DataFrame thô -> load.py đẩy vào BigQuery raw.cards
"""
import pandas as pd
from pathlib import Path


def extract(csv_path: Path) -> pd.DataFrame:
    """Đọc CSV thô, KHÔNG transform logic ở đây, chỉ đọc + cast type cơ bản nếu cần."""
    # TODO: implement
    raise NotImplementedError
