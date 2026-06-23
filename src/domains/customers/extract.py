import sqlite3
import pandas as pd
from pathlib import Path

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def extract_customers() -> pd.DataFrame:
    """Đọc toàn bộ bảng customers từ SQLite."""
    db_path = Path(settings.sqlite_db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite DB không tồn tại: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql("SELECT * FROM customers", conn)

    logger.info("Extracted customers | rows=%d", len(df))
    return df