"""
Analytics Service — Business logic for market analytics and provider rankings.

Functions:
  - get_market_average()           → Average test/package prices, totals
  - get_provider_rankings()        → All providers ranked by avg test price
  - get_cheapest_provider()        → Provider with lowest average test price
  - get_most_expensive_provider()  → Provider with highest average test price
"""

import logging
from typing import Optional

from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.database.models import Provider, TestPricing, PackagePricing
from app.schemas.schemas import (
    MarketAnalyticsResponse,
    CompetitorAnalyticsResponse,
    ProviderRanking,
    DashboardResponse,
)

logger = logging.getLogger(__name__)


def get_market_average(db: Session) -> MarketAnalyticsResponse:
    """
    Compute aggregate market analytics from the database.
    """
    logger.info("Computing market analytics")

    # Average test price
    avg_test = db.query(func.avg(TestPricing.price)).filter(
        TestPricing.price.isnot(None)
    ).scalar()

    # Average package price
    avg_pkg = db.query(func.avg(PackagePricing.package_price)).filter(
        PackagePricing.package_price.isnot(None)
    ).scalar()

    # Total providers
    total_providers = db.query(func.count(Provider.provider_id)).scalar() or 0

    # Total test pricing rows
    total_tests = db.query(func.count(TestPricing.pricing_id)).scalar() or 0

    # Total unique test names
    total_unique_tests = db.query(
        func.count(distinct(TestPricing.test_name))
    ).scalar() or 0

    # Total packages
    total_packages = db.query(func.count(PackagePricing.package_id)).scalar() or 0

    # Distinct cities
    cities_result = db.query(distinct(Provider.city)).filter(
        Provider.city.isnot(None)
    ).all()
    cities = sorted([c[0] for c in cities_result if c[0]])

    # Distinct categories
    categories_result = db.query(distinct(TestPricing.category)).filter(
        TestPricing.category.isnot(None)
    ).all()
    categories = sorted([c[0] for c in categories_result if c[0]])

    return MarketAnalyticsResponse(
        average_test_price=round(float(avg_test), 2) if avg_test else None,
        average_package_price=round(float(avg_pkg), 2) if avg_pkg else None,
        total_providers=total_providers,
        total_packages=total_packages,
        total_tests=total_tests,
        total_unique_test_names=total_unique_tests,
        total_cities=len(cities),
        cities=cities,
        categories=categories,
    )


def get_provider_rankings(db: Session) -> list[ProviderRanking]:
    """
    Rank all providers by their average test price (ascending — cheapest first).
    """
    logger.info("Computing provider rankings")

    results = (
        db.query(
            Provider.provider_name,
            Provider.city,
            func.avg(TestPricing.price).label("avg_price"),
            func.count(TestPricing.pricing_id).label("test_count"),
        )
        .join(TestPricing, Provider.provider_id == TestPricing.provider_id)
        .filter(TestPricing.price.isnot(None))
        .group_by(Provider.provider_name, Provider.city)
        .order_by(func.avg(TestPricing.price).asc())
        .all()
    )

    rankings = []
    for name, city, avg_price, test_count in results:
        rankings.append(
            ProviderRanking(
                provider_name=name,
                city=city,
                average_test_price=round(float(avg_price), 2) if avg_price else None,
                total_tests_offered=test_count,
            )
        )

    return rankings


def get_cheapest_provider(db: Session) -> Optional[ProviderRanking]:
    """
    Return the provider with the lowest average test price.
    """
    rankings = get_provider_rankings(db)
    return rankings[0] if rankings else None


def get_most_expensive_provider(db: Session) -> Optional[ProviderRanking]:
    """
    Return the provider with the highest average test price.
    """
    rankings = get_provider_rankings(db)
    return rankings[-1] if rankings else None


def get_competitor_analytics(db: Session) -> CompetitorAnalyticsResponse:
    """
    Full competitor analytics: cheapest, most expensive, and all rankings.
    """
    rankings = get_provider_rankings(db)

    return CompetitorAnalyticsResponse(
        cheapest_provider=rankings[0] if rankings else None,
        most_expensive_provider=rankings[-1] if rankings else None,
        provider_rankings=rankings,
    )


def get_dashboard_summary(db: Session) -> DashboardResponse:
    """
    Aggregated dashboard summary combining market analytics and competitor data.
    """
    logger.info("Computing dashboard summary")

    market = get_market_average(db)
    cheapest = get_cheapest_provider(db)
    most_expensive = get_most_expensive_provider(db)

    return DashboardResponse(
        total_providers=market.total_providers,
        total_tests=market.total_tests,
        total_packages=market.total_packages,
        total_cities=market.total_cities,
        average_test_price=market.average_test_price,
        average_package_price=market.average_package_price,
        categories=market.categories,
        cities=market.cities,
        cheapest_provider=f"{cheapest.provider_name} ({cheapest.city})" if cheapest else None,
        most_expensive_provider=f"{most_expensive.provider_name} ({most_expensive.city})" if most_expensive else None,
    )
