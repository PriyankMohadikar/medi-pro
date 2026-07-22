"""
Seed script: Add new test/service catalog items to the test_pricing table.

Inserts 7 new items for all ES Healthcare provider locations.
Uses upsert logic — safe to run multiple times (skips existing entries).

Usage:
    cd backend
    python seed_new_tests.py
"""

import logging
from config import load_settings
from database import get_engine, get_session_factory
from models import Provider, TestPricing

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s")
logger = logging.getLogger("seed_new_tests")

# ---------------------------------------------------------------------------
# New catalog items to add
# ---------------------------------------------------------------------------
NEW_TESTS = [
    {"test_name": "Testosterone",              "category": "Hormones",            "price": 550},
    {"test_name": "Prolactin",                 "category": "Hormones",            "price": 450},
    {"test_name": "LH (Luteinizing Hormone)",  "category": "Hormones",            "price": 450},
    {"test_name": "Iron Profile",              "category": "Nutrition",            "price": 1200},
    {"test_name": "ECG",                       "category": "Cardiology",           "price": 150},
    {"test_name": "Doctor Consultation",       "category": "Consultation",         "price": 400},
    {"test_name": "Breakfast",                 "category": "Additional Services",  "price": 150},
]

ES_PROVIDER_NAME = "ES Healthcare"


def seed():
    settings = load_settings()
    engine = get_engine(settings)
    SessionFactory = get_session_factory(engine)
    session = SessionFactory()

    try:
        # Find all ES Healthcare providers (one per city)
        es_providers = (
            session.query(Provider)
            .filter(Provider.provider_name == ES_PROVIDER_NAME)
            .order_by(Provider.city)
            .all()
        )

        if not es_providers:
            logger.error(f"No providers found with name '{ES_PROVIDER_NAME}'. Aborting.")
            return

        logger.info(f"Found {len(es_providers)} ES Healthcare locations:")
        for p in es_providers:
            logger.info(f"  ID={p.provider_id}, City={p.city}")

        inserted = 0
        skipped = 0

        for provider in es_providers:
            for test in NEW_TESTS:
                # Check if this test already exists for this provider (upsert logic)
                existing = (
                    session.query(TestPricing)
                    .filter_by(
                        provider_id=provider.provider_id,
                        test_name=test["test_name"],
                    )
                    .first()
                )

                if existing:
                    logger.debug(
                        f"  SKIP (exists): {provider.city} / {test['test_name']}"
                    )
                    skipped += 1
                    continue

                # Insert new test pricing row
                new_row = TestPricing(
                    provider_id=provider.provider_id,
                    test_name=test["test_name"],
                    category=test["category"],
                    price=test["price"],
                )
                session.add(new_row)
                inserted += 1
                logger.info(
                    f"  INSERT: {provider.city} / {test['test_name']} "
                    f"({test['category']}) = Rs.{test['price']}"
                )

        session.commit()
        logger.info(f"Seed complete: {inserted} inserted, {skipped} skipped (already exist).")

    except Exception as e:
        session.rollback()
        logger.error(f"Seed failed: {e}", exc_info=True)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
