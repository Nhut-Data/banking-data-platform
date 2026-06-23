import sqlite3
import pandas as pd
from pathlib import Path

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def extract_cards() -> pd.DataFrame:
    with sqlite3.connect(Path(settings.sqlite_db_path)) as conn:
        df = pd.read_sql("SELECT * FROM cards", conn)
    logger.info("Extracted cards | rows=%d", len(df))
    return df
