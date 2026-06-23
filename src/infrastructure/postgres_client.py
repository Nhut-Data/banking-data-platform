from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.banking_db_url,
            pool_pre_ping=True,   # verify connection trước khi dùng
            pool_size=5,
            max_overflow=10,
        )
        logger.info("PostgreSQL engine created | db=%s", settings.banking_db_name)
    return _engine


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager — tự động commit hoặc rollback."""
    SessionLocal = sessionmaker(bind=get_engine())
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def health_check() -> bool:
    """Verify connect được PostgreSQL banking_db."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("PostgreSQL health check failed: %s", e)
        return False