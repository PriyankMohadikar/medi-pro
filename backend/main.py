"""
Healthcare Pricing Data Layer — Main Entry Point

Orchestrates the full ETL pipeline:
  1. Load configuration
  2. Ensure database exists
  3. Create tables
  4. Run Excel ETL
  5. Print summary
  6. Log execution time
"""

import sys
import time
import logging
from pathlib import Path

from config import load_settings
from database import (
    create_tables,
    ensure_database_exists,
    get_engine,
    get_session_factory,
    test_connection,
)
from excel_etl import ExcelETL
from utils import setup_logging

logger = logging.getLogger(__name__)

# Path to the Excel dataset
# First check inside backend/data/, then fallback to Desktop
EXCEL_FILENAME = "dataset_web.xlsx"
BACKEND_DIR = Path(__file__).resolve().parent


def find_excel_file() -> Path:
    """
    Locate the dataset Excel file.

    Search order:
      1. backend/data/dataset_web.xlsx (project copy)
      2. backend/dataset_web.xlsx
      3. Desktop/dataset_web.xlsx (original location)
    """
    search_paths = [
        BACKEND_DIR / "data" / EXCEL_FILENAME,
        BACKEND_DIR / EXCEL_FILENAME,
        Path.home() / "Desktop" / EXCEL_FILENAME,
    ]

    for path in search_paths:
        if path.exists():
            logger.info(f"Found Excel file: {path}")
            return path

    raise FileNotFoundError(
        f"Could not find '{EXCEL_FILENAME}' in any expected location. "
        f"Searched: {[str(p) for p in search_paths]}"
    )


def print_summary(stats, elapsed: float) -> None:
    """Print a formatted import summary to the console."""
    print("\n" + "=" * 55)
    print("  HEALTHCARE PRICING ETL — IMPORT SUMMARY")
    print("=" * 55)
    print(f"  Providers Imported     : {stats.providers_imported}")
    print(f"  Test Pricing Imported  : {stats.test_pricing_imported}")
    print(f"  Package Pricing Imported: {stats.package_pricing_imported}")
    print(f"  Package Tests Imported : {stats.package_tests_imported}")
    print(f"  Duplicates Removed     : {stats.duplicates_removed}")
    print(f"  Rows Skipped           : {stats.rows_skipped}")

    if stats.errors:
        print(f"  Errors                 : {len(stats.errors)}")
        for err in stats.errors[:5]:
            print(f"    ⚠ {err}")
        if len(stats.errors) > 5:
            print(f"    ... and {len(stats.errors) - 5} more errors")

    print(f"  Execution Time         : {elapsed:.2f}s")
    print("=" * 55)
    print("  ✔ Execution Completed Successfully")
    print("=" * 55 + "\n")


def main() -> None:
    """Main entry point for the Healthcare Pricing ETL pipeline."""
    start_time = time.time()

    # --- 1. Setup logging ---
    setup_logging()
    logger.info("=" * 60)
    logger.info("Healthcare Pricing ETL Pipeline — Starting")
    logger.info("=" * 60)

    try:
        # --- 2. Load configuration ---
        settings = load_settings()
        logger.info(
            f"Configuration loaded — Target DB: {settings.DB_NAME} "
            f"@ {settings.DB_HOST}:{settings.DB_PORT}"
        )

        # --- 3. Ensure database exists ---
        ensure_database_exists(settings)

        # --- 4. Create engine & verify connection ---
        engine = get_engine(settings)
        test_connection(engine)

        # --- 5. Create tables ---
        create_tables(engine)

        # --- 6. Find Excel file ---
        excel_path = find_excel_file()
        print(f"✔ Excel file found: {excel_path.name}")

        # --- 7. Run ETL within a transaction ---
        SessionFactory = get_session_factory(engine)
        session = SessionFactory()

        try:
            etl = ExcelETL(session, excel_path)
            stats = etl.run()

            # Commit only on full success
            session.commit()
            logger.info("Transaction committed successfully")

        except Exception as e:
            session.rollback()
            logger.error(f"ETL failed, transaction rolled back: {e}")
            raise

        finally:
            session.close()

        # --- 8. Print summary ---
        elapsed = time.time() - start_time
        print_summary(stats, elapsed)

        logger.info(f"Pipeline completed in {elapsed:.2f}s")
        logger.info("=" * 60)

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\n✘ Error: {e}")
        sys.exit(1)

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Pipeline failed after {elapsed:.2f}s: {e}", exc_info=True)
        print(f"\n✘ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
