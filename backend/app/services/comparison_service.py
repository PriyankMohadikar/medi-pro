"""
Comparison Service — Business logic for comparing test and package prices.

Functions:
  - compare_test_prices()   → Compare multiple test prices across providers
  - compare_package_prices() → Compare a single package across providers
"""

import logging
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Provider, TestPricing, PackagePricing, PackageTest
from app.schemas.schemas import (
    CompareTestsResponse,
    ComparePackagesResponse,
    ProviderTestComparison,
    ProviderPackageComparison,
)

logger = logging.getLogger(__name__)


def compare_test_prices(
    db: Session,
    test_names: list[str],
    city: Optional[str] = None,
) -> CompareTestsResponse:
    """
    Compare prices for a list of tests across all providers.

    For each provider, retrieves the price of each requested test.
    Calculates total cost per provider, lowest, highest, and market average.
    """
    logger.info(f"Comparing tests: {test_names}, city={city}")

    # Build base query
    query = (
        db.query(
            Provider.provider_name,
            Provider.city,
            TestPricing.test_name,
            TestPricing.price,
        )
        .join(TestPricing, Provider.provider_id == TestPricing.provider_id)
        .filter(TestPricing.test_name.in_(test_names))
    )

    if city:
        query = query.filter(func.lower(Provider.city) == city.lower())

    results = query.all()

    if not results:
        return CompareTestsResponse(
            tests_requested=test_names,
            city_filter=city,
            providers=[],
        )

    # Group by provider
    provider_data: dict[str, ProviderTestComparison] = {}
    for provider_name, prov_city, test_name, price in results:
        key = f"{provider_name}|{prov_city}"
        if key not in provider_data:
            provider_data[key] = ProviderTestComparison(
                provider_name=provider_name,
                city=prov_city,
                prices={},
                total_price=0.0,
            )
        price_float = float(price) if price is not None else None
        provider_data[key].prices[test_name] = price_float

    # Calculate totals
    for comp in provider_data.values():
        valid_prices = [p for p in comp.prices.values() if p is not None]
        comp.total_price = round(sum(valid_prices), 2)

    providers_list = list(provider_data.values())

    # Only consider providers with at least one priced test
    priced_providers = [p for p in providers_list if p.total_price > 0]

    lowest = min(priced_providers, key=lambda p: p.total_price, default=None)
    highest = max(priced_providers, key=lambda p: p.total_price, default=None)

    all_totals = [p.total_price for p in priced_providers]
    avg_price = round(sum(all_totals) / len(all_totals), 2) if all_totals else None

    return CompareTestsResponse(
        tests_requested=test_names,
        city_filter=city,
        providers=providers_list,
        lowest_total=lowest.total_price if lowest else None,
        lowest_provider=lowest.provider_name if lowest else None,
        highest_total=highest.total_price if highest else None,
        highest_provider=highest.provider_name if highest else None,
        average_market_price=avg_price,
    )


def compare_package_prices(
    db: Session,
    package_name: str,
    city: Optional[str] = None,
) -> ComparePackagesResponse:
    """
    Compare a single package across all providers.

    Returns each provider's price and included tests, along with
    lowest, highest, and average pricing.
    """
    logger.info(f"Comparing package: {package_name}, city={city}")

    query = (
        db.query(PackagePricing)
        .join(Provider, PackagePricing.provider_id == Provider.provider_id)
        .filter(func.lower(PackagePricing.package_name) == package_name.lower())
    )

    if city:
        query = query.filter(func.lower(Provider.city) == city.lower())

    packages = query.all()

    if not packages:
        return ComparePackagesResponse(
            package_name=package_name,
            city_filter=city,
            providers=[],
        )

    providers_list = []
    for pkg in packages:
        tests_included = [t.test_name for t in pkg.tests if t.test_name]
        providers_list.append(
            ProviderPackageComparison(
                provider_name=pkg.provider.provider_name if pkg.provider else "Unknown",
                city=pkg.provider.city if pkg.provider else None,
                package_price=float(pkg.package_price) if pkg.package_price else None,
                tests_included=tests_included,
            )
        )

    priced = [p for p in providers_list if p.package_price is not None]

    lowest = min(priced, key=lambda p: p.package_price, default=None)
    highest = max(priced, key=lambda p: p.package_price, default=None)

    all_prices = [p.package_price for p in priced]
    avg_price = round(sum(all_prices) / len(all_prices), 2) if all_prices else None

    return ComparePackagesResponse(
        package_name=package_name,
        city_filter=city,
        providers=providers_list,
        lowest_price=lowest.package_price if lowest else None,
        lowest_provider=lowest.provider_name if lowest else None,
        highest_price=highest.package_price if highest else None,
        highest_provider=highest.provider_name if highest else None,
        average_price=avg_price,
    )
