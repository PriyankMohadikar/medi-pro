"""
Excel ETL pipeline for Healthcare Pricing data.

Reads dataset_web.xlsx, cleans and normalizes the data,
then populates the PostgreSQL database through SQLAlchemy ORM.

Key transformations:
  - ES Price & Competitor Price → separate normalized rows
  - Package 'Tests Included' → individual package_tests rows
  - City, test name, provider name standardization
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from models import PackagePricing, PackageTest, Provider, TestPricing
from utils import (
    clean_price,
    clean_value,
    classify_provider_type,
    standardize_city,
    standardize_provider_name,
    standardize_test_name,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Import Statistics Tracker
# ---------------------------------------------------------------------------


@dataclass
class ImportStats:
    """Tracks counts for the ETL summary report."""

    providers_imported: int = 0
    test_pricing_imported: int = 0
    package_pricing_imported: int = 0
    package_tests_imported: int = 0
    duplicates_removed: int = 0
    rows_skipped: int = 0
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Excel ETL Pipeline
# ---------------------------------------------------------------------------


class ExcelETL:
    """
    Orchestrates the full ETL pipeline from Excel to PostgreSQL.

    Usage:
        etl = ExcelETL(session, excel_path)
        stats = etl.run()
    """

    # Name used for the in-house provider (ES Price column)
    ES_PROVIDER_NAME = "ES Healthcare"
    ES_PROVIDER_TYPE = "Healthcare Centre"

    def __init__(self, session: Session, excel_path: Path):
        self.session = session
        self.excel_path = excel_path
        self.stats = ImportStats()
        # Cache of (provider_name, city) → Provider ORM instance
        self._provider_cache: dict[tuple[str, str], Provider] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> ImportStats:
        """
        Execute the full ETL pipeline.

        Reads both Excel sheets, cleans data, and inserts into the database.
        All operations run within the caller's session/transaction.
        """
        logger.info(f"Starting ETL from: {self.excel_path}")

        # --- Individual Pricing ---
        df_individual = self._read_sheet("Individual pricing_Cleaned")
        if df_individual is not None:
            self._process_individual_pricing(df_individual)

        # --- Package Pricing ---
        df_packages = self._read_sheet("package_pricing")
        if df_packages is not None:
            self._process_package_pricing(df_packages)

        # Flush to DB (still within the transaction)
        self.session.flush()

        logger.info(
            f"ETL completed — Providers: {self.stats.providers_imported}, "
            f"Tests: {self.stats.test_pricing_imported}, "
            f"Packages: {self.stats.package_pricing_imported}, "
            f"Package Tests: {self.stats.package_tests_imported}, "
            f"Duplicates Removed: {self.stats.duplicates_removed}, "
            f"Rows Skipped: {self.stats.rows_skipped}"
        )

        return self.stats

    # ------------------------------------------------------------------
    # Sheet Reading
    # ------------------------------------------------------------------

    def _read_sheet(self, sheet_name: str) -> pd.DataFrame | None:
        """Read a single sheet from the Excel file."""
        try:
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            # Strip whitespace from column names
            df.columns = df.columns.str.strip()
            logger.info(f"Read sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            msg = f"Failed to read sheet '{sheet_name}': {e}"
            logger.error(msg)
            self.stats.errors.append(msg)
            return None

    # ------------------------------------------------------------------
    # Individual Pricing ETL
    # ------------------------------------------------------------------

    def _process_individual_pricing(self, df: pd.DataFrame) -> None:
        """
        Process the 'Individual pricing_Cleaned' sheet.

        Each row is normalized into TWO records:
          1. ES Healthcare provider with ES Price
          2. Competitor provider with Competitor Price
        """
        logger.info("Processing individual pricing data...")

        # --- Data Cleaning ---
        original_count = len(df)

        # Remove completely empty rows
        df = df.dropna(how="all")

        # Remove duplicate rows
        before_dedup = len(df)
        df = df.drop_duplicates()
        dups_removed = before_dedup - len(df)
        self.stats.duplicates_removed += dups_removed
        if dups_removed > 0:
            logger.info(f"Removed {dups_removed} duplicate rows from individual pricing")

        empty_removed = original_count - before_dedup
        if empty_removed > 0:
            logger.info(f"Removed {empty_removed} empty rows from individual pricing")

        for idx, row in df.iterrows():
            try:
                # Clean and standardize values
                test_name = standardize_test_name(clean_value(row.get("Test Name")))
                category = clean_value(row.get("Category"))
                city = standardize_city(clean_value(row.get("City")))
                es_price = clean_price(row.get("ES Price (₹)"))
                competitor_name = standardize_provider_name(clean_value(row.get("Competitor")))
                competitor_type = classify_provider_type(
                    clean_value(row.get("Healthcare/Diagnostic/ Labs"))
                )
                competitor_price = clean_price(row.get("Competitor Price (₹)"))

                if not test_name or not city:
                    self.stats.rows_skipped += 1
                    logger.debug(f"Skipped row {idx}: missing test_name or city")
                    continue

                # --- Row 1: ES Healthcare ---
                es_provider = self._get_or_create_provider(
                    name=self.ES_PROVIDER_NAME,
                    provider_type=self.ES_PROVIDER_TYPE,
                    city=city,
                )

                if es_price is not None:
                    self._insert_test_pricing(
                        provider=es_provider,
                        test_name=test_name,
                        category=category,
                        price=es_price,
                    )

                # --- Row 2: Competitor ---
                if competitor_name:
                    comp_provider = self._get_or_create_provider(
                        name=competitor_name,
                        provider_type=competitor_type,
                        city=city,
                    )

                    if competitor_price is not None:
                        self._insert_test_pricing(
                            provider=comp_provider,
                            test_name=test_name,
                            category=category,
                            price=competitor_price,
                        )

            except Exception as e:
                msg = f"Error processing individual pricing row {idx}: {e}"
                logger.error(msg)
                self.stats.errors.append(msg)
                self.stats.rows_skipped += 1

        logger.info(f"Individual pricing processing complete")

    # ------------------------------------------------------------------
    # Package Pricing ETL
    # ------------------------------------------------------------------

    def _process_package_pricing(self, df: pd.DataFrame) -> None:
        """
        Process the 'package_pricing' sheet.

        Inserts providers, packages, and splits 'Tests Included'
        into individual package_tests rows.
        """
        logger.info("Processing package pricing data...")

        # --- Data Cleaning ---
        original_count = len(df)

        df = df.dropna(how="all")

        before_dedup = len(df)
        df = df.drop_duplicates()
        dups_removed = before_dedup - len(df)
        self.stats.duplicates_removed += dups_removed
        if dups_removed > 0:
            logger.info(f"Removed {dups_removed} duplicate rows from package pricing")

        for idx, row in df.iterrows():
            try:
                city = standardize_city(clean_value(row.get("City")))
                provider_type = classify_provider_type(clean_value(row.get("Type")))
                provider_name = standardize_provider_name(
                    clean_value(row.get("Provider Name"))
                )
                package_name = clean_value(row.get("Package Name"))
                package_price = clean_price(row.get("Package Price (₹)"))
                tests_included = clean_value(row.get("Tests Included"))

                if not provider_name or not package_name:
                    self.stats.rows_skipped += 1
                    logger.debug(f"Skipped package row {idx}: missing provider or package name")
                    continue

                # --- Provider ---
                provider = self._get_or_create_provider(
                    name=provider_name,
                    provider_type=provider_type,
                    city=city,
                )

                # --- Package ---
                package, is_new = self._insert_package_pricing(
                    provider=provider,
                    package_name=package_name,
                    package_price=package_price,
                )

                if package is None:
                    continue

                # --- Package Tests (split comma-separated) ---
                # Only insert tests for newly created packages to avoid
                # duplicates on re-runs
                if is_new and tests_included:
                    test_names = [t.strip() for t in str(tests_included).split(",")]
                    for raw_test_name in test_names:
                        std_test_name = standardize_test_name(raw_test_name)
                        if std_test_name:
                            pkg_test = PackageTest(
                                package_id=package.package_id,
                                test_name=std_test_name,
                            )
                            self.session.add(pkg_test)
                            self.stats.package_tests_imported += 1

            except Exception as e:
                msg = f"Error processing package row {idx}: {e}"
                logger.error(msg)
                self.stats.errors.append(msg)
                self.stats.rows_skipped += 1

        logger.info(f"Package pricing processing complete")

    # ------------------------------------------------------------------
    # Provider Management
    # ------------------------------------------------------------------

    def _get_or_create_provider(
        self, name: str, provider_type: str | None, city: str | None
    ) -> Provider:
        """
        Get an existing provider or create a new one.

        Uses an in-memory cache to avoid redundant DB queries.
        Providers are unique by (provider_name, city).
        """
        cache_key = (name, city)

        if cache_key in self._provider_cache:
            return self._provider_cache[cache_key]

        # Check database
        existing = (
            self.session.query(Provider)
            .filter_by(provider_name=name, city=city)
            .first()
        )

        if existing:
            self._provider_cache[cache_key] = existing
            return existing

        # Create new provider
        provider = Provider(
            provider_name=name,
            provider_type=provider_type,
            city=city,
        )
        self.session.add(provider)
        self.session.flush()  # Get the generated provider_id

        self._provider_cache[cache_key] = provider
        self.stats.providers_imported += 1
        logger.debug(f"Created provider: {name} ({city})")

        return provider

    # ------------------------------------------------------------------
    # Test Pricing Insertion
    # ------------------------------------------------------------------

    def _insert_test_pricing(
        self,
        provider: Provider,
        test_name: str,
        category: str | None,
        price: float,
    ) -> None:
        """
        Insert a test pricing record, skipping duplicates.

        Unique constraint: (provider_id, test_name)
        """
        existing = (
            self.session.query(TestPricing)
            .filter_by(provider_id=provider.provider_id, test_name=test_name)
            .first()
        )

        if existing:
            # Update price if it changed (upsert behavior)
            if existing.price != price:
                existing.price = price
                existing.category = category
                logger.debug(
                    f"Updated test pricing: {provider.provider_name} / {test_name} = {price}"
                )
            return

        test_pricing = TestPricing(
            provider_id=provider.provider_id,
            test_name=test_name,
            category=category,
            price=price,
        )
        self.session.add(test_pricing)
        self.stats.test_pricing_imported += 1

    # ------------------------------------------------------------------
    # Package Pricing Insertion
    # ------------------------------------------------------------------

    def _insert_package_pricing(
        self,
        provider: Provider,
        package_name: str,
        package_price: float | None,
    ) -> tuple[PackagePricing | None, bool]:
        """
        Insert a package pricing record, skipping duplicates.

        Unique constraint: (provider_id, package_name)
        Returns a tuple of (PackagePricing instance, is_new).
        """
        existing = (
            self.session.query(PackagePricing)
            .filter_by(provider_id=provider.provider_id, package_name=package_name)
            .first()
        )

        if existing:
            logger.debug(
                f"Skipped duplicate package: {provider.provider_name} / {package_name}"
            )
            return existing, False

        package = PackagePricing(
            provider_id=provider.provider_id,
            package_name=package_name,
            package_price=package_price,
        )
        self.session.add(package)
        self.session.flush()  # Get generated package_id
        self.stats.package_pricing_imported += 1

        return package, True
