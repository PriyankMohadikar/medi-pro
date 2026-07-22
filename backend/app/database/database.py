"""
Database connection and session management.

Provides:
  - SQLAlchemy engine creation
  - Session factory and dependency injection for FastAPI
  - Connection testing

IMPORTANT: Does NOT call Base.metadata.create_all().
           The database and tables already exist.
"""

import logging
from urllib.parse import urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from config import load_settings, mask_database_url

logger = logging.getLogger(__name__)

# Load settings once at module level
settings = load_settings()

masked_url = mask_database_url(settings.database_url)
logger.info(f"[APP DB INIT] Target Database URL: {masked_url}")

# Create engine
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """
    Verify the database connection is working.
    Returns True if connection succeeds.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[OK] Database connection verified")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

