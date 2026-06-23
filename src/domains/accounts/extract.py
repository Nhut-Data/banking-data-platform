import sqlite3
import pandas as pd
from pathlib import Path

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def extract_accounts() -> pd.DataFrame:
    with sqlite3.connect(Path(settings.sqlite_db_path)) as conn:
        df = pd.read_sql("SELECT * FROM accounts", conn)
    logger.info("Extracted accounts | rows=%d", len(df))
    return df