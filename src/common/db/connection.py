"""
SIE Analytics — Database Connection Factory.

All agents must use this module for database connections:

    from src.common.db.connection import get_engine, get_session, SessionLocal

Usage patterns:

    # Pattern 1: Context manager (recommended for scripts/tests)
    with get_session() as session:
        suppliers = session.query(DimSupplier).all()

    # Pattern 2: FastAPI dependency injection
    def get_db():
        with get_session() as session:
            yield session

    # Pattern 3: Direct session (for Airflow operators)
    session = SessionLocal()
    try:
        ...
        session.commit()
    finally:
        session.close()
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.common.config import settings

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Engine (singleton per process)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_engine: Engine | None = None


def get_engine() -> Engine:
    """
    Get or create the SQLAlchemy engine (singleton).

    Uses connection pooling with settings from config.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.db.url,
            pool_size=settings.db.POOL_SIZE,
            max_overflow=settings.db.MAX_OVERFLOW,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections every hour
            echo=False,
        )
        logger.info("Database engine created: %s:%s/%s", settings.db.HOST, settings.db.PORT, settings.db.NAME)
    return _engine


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Session Factory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=None,  # Bound lazily via init_session_factory()
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def init_session_factory() -> None:
    """Bind the session factory to the engine. Call once at app startup."""
    SessionLocal.configure(bind=get_engine())
    logger.info("Session factory initialized")


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager that provides a transactional database session.

    Automatically commits on success, rolls back on exception, and closes.

    Usage:
        with get_session() as session:
            session.add(new_record)
            # auto-commits here
    """
    # Ensure factory is bound
    if SessionLocal.kw.get("bind") is None:
        init_session_factory()

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Health Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def check_db_health() -> dict:
    """
    Check database connectivity and return status.

    Returns:
        dict with keys: "status" ("healthy" | "unhealthy"), "details"
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

            # Check TimescaleDB extension
            tsdb = conn.execute(
                text("SELECT installed_version FROM pg_available_extensions WHERE name = 'timescaledb'")
            ).fetchone()

        return {
            "status": "healthy",
            "details": {
                "host": settings.db.HOST,
                "port": settings.db.PORT,
                "database": settings.db.NAME,
                "timescaledb": tsdb[0] if tsdb else "not installed",
                "pool_size": settings.db.POOL_SIZE,
            },
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "details": {"error": str(e)},
        }
