from datetime import timezone, datetime
import pandas as pd

from src.domains.customers.schema import CustomerRaw
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate từng row bằng Pydantic, drop row lỗi + log.
    Không làm heavy transform ở đây — để BigQuery SQL xử lý.
    """
    valid_rows = []
    error_count = 0

    for row in df.to_dict(orient="records"):
        try:
            CustomerRaw(**row)
            valid_rows.append(row)
        except Exception as e:
            error_count += 1
            logger.warning("Invalid customer row | id=%s | error=%s",
                           row.get("customer_id"), e)

    if error_count:
        logger.warning("Dropped %d invalid rows out of %d", error_count, len(df))

    result = pd.DataFrame(valid_rows)
    result["_ingested_at"] = datetime.now(timezone.utc)
    logger.info("Transformed customers | valid_rows=%d", len(result))
    return result