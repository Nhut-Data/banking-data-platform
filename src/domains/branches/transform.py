from datetime import timezone, datetime
import pandas as pd

from src.domains.branches.schema import BranchRaw
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def transform_branches(df: pd.DataFrame) -> pd.DataFrame:
    # Replace NaN → None để Pydantic nhận đúng Optional field
    df = df.where(pd.notna(df), None)

    valid_rows, error_count = [], 0
    for row in df.to_dict(orient="records"):
        try:
            BranchRaw(**row)
            valid_rows.append(row)
        except Exception as e:
            error_count += 1
            logger.warning("Invalid branch row | id=%s | error=%s",
                           row.get("branch_id"), e)
    if error_count:
        logger.warning("Dropped %d invalid rows out of %d", error_count, len(df))
    result = pd.DataFrame(valid_rows)
    result["_ingested_at"] = datetime.now(timezone.utc)
    logger.info("Transformed branches | valid_rows=%d", len(result))
    return result
