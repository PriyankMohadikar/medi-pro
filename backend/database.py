"""
Database connection and management module.

Handles:
  - Automatic creation of the target database if it doesn't exist
  - SQLAlchemy engine and session factory
  - Table creation via ORM metadata
"""

import logging

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from config import Settings, mask_database_url
from models import Base
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def ensure_database_exists(settings: Settings) -> None:
    """
    Check if the target database exists; create it if it doesn't.
    Skips database creation if DATABASE_URL (e.g. Supabase) is provided.
    """
    if settings.DATABASE_URL:
        logger.info("Using explicit DATABASE_URL (Supabase/Cloud DB); skipping local CREATE DATABASE check.")
        return

    conn = None
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dbname="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (settings.DB_NAME,),
            )
            exists = cur.fetchone()

            if not exists:
                cur.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
                logger.info(f"Database '{settings.DB_NAME}' created successfully")
                print(f"[OK] Database '{settings.DB_NAME}' created")
            else:
                logger.info(f"Database '{settings.DB_NAME}' already exists")

    except psycopg2.Error as e:
        logger.warning(f"Could not auto-create database (may be a cloud DB / restricted user): {e}")
    finally:
        if conn:
            conn.close()


def get_engine(settings: Settings):
    """
    Create and return a SQLAlchemy engine for the target database.
    Logs masked connection information for runtime verification.
    """
    db_url = settings.database_url
    masked_url = mask_database_url(db_url)
    logger.info(f"[DB INIT] Target Database URL: {masked_url}")

    try:
        parsed = urlparse(db_url)
        host = parsed.hostname or settings.DB_HOST
        port = parsed.port or settings.DB_PORT
        user = parsed.username or settings.DB_USER
        dbname = parsed.path.lstrip("/") or settings.DB_NAME
        logger.info(f"[DB CONFIG] User: {user} | Host: {host}:{port} | Database: {dbname}")
    except Exception as e:
        logger.warning(f"[DB CONFIG] Could not parse DB URL metadata: {e}")

    engine = create_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    return engine


def get_session_factory(engine) -> sessionmaker:
    """
    Create and return a SQLAlchemy session factory bound to the engine.
    """
    return sessionmaker(bind=engine, expire_on_commit=False)


def create_tables(engine) -> None:
    """
    Create all ORM-defined tables if they don't already exist.
    Uses CREATE TABLE IF NOT EXISTS under the hood.
    """
    Base.metadata.create_all(engine)
    logger.info("All database tables created/verified successfully")
    print("[OK] Tables Created Successfully")


def test_connection(engine) -> bool:
    """
    Verify the database connection is working.
    Returns True if connection succeeds.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[OK] Database connection verified successfully")
        print("[OK] Database Connected")
        return True
    except Exception as e:
        err_msg = str(e)
        logger.error(f"[DB ERROR] Database connection failed: {err_msg}")
        if "password authentication failed" in err_msg.lower():
            logger.error(
                "[DB DIAGNOSTIC] Authentication failed! Check:\n"
                "  1. Username on port 6543 MUST be in format 'postgres.<project_ref>' (e.g. postgres.bnccejadsruqxkniiwrn)\n"
                "  2. Special characters in password must be URL encoded (e.g. %21 for '!').\n"
                "  3. No surrounding quotes or extra line breaks in DATABASE_URL."
            )
        elif "could not connect" in err_msg.lower() or "timeout" in err_msg.lower() or "refused" in err_msg.lower():
            logger.error(
                "[DB DIAGNOSTIC] Network unreachable! Check:\n"
                "  1. Use port 6543 pooler (aws-0-ap-southeast-1.pooler.supabase.com) for Supabase IPv4 support.\n"
                "  2. Ensure sslmode=require is appended to the connection string."
            )
        raise

