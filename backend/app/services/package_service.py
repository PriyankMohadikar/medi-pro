"""
Package Service — Business logic for custom package building.

Functions:
  - build_custom_package() → Build a custom package from selected tests
"""

import logging
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Provider, TestPricing
from app.schemas.schemas import (
    CustomPackageRequest,
    CustomPackageResponse,
    CustomPackageTestDetail,
)

logger = logging.getLogger(__name__)


def build_custom_package(
    db: Session,
    request: CustomPackageRequest,
) -> CustomPackageResponse:
    """
    Build a custom package from a list of test names.

    For each test:
      - Finds the average price across all providers (optionally filtered by city)
      - Finds the cheapest provider and price

    Then calculates:
      - Total cost (sum of cheapest prices)
      - Suggested package price (with margin applied)
      - Expected profit
      - Market average total
    """
    logger.info(f"Building custom package: tests={request.tests}, city={request.city}, margin={request.margin}%")

    test_details: list[CustomPackageTestDetail] = []
    total_cost = 0.0
    market_avg_total = 0.0

    for test_name in request.tests:
        query = (
            db.query(
                TestPricing.price,
                Provider.provider_name,
            )
            .join(Provider, TestPricing.provider_id == Provider.provider_id)
            .filter(func.lower(TestPricing.test_name) == test_name.lower())
            .filter(TestPricing.price.isnot(None))
        )

        if request.city:
            query = query.filter(func.lower(Provider.city) == request.city.lower())

        results = query.all()

        if not results:
            test_details.append(
                CustomPackageTestDetail(
                    test_name=test_name,
                    avg_price=None,
                    cheapest_price=None,
                    cheapest_provider=None,
                )
            )
            continue

        prices = [(float(r.price), r.provider_name) for r in results]
        avg_price = round(sum(p[0] for p in prices) / len(prices), 2)
        cheapest = min(prices, key=lambda x: x[0])

        test_details.append(
            CustomPackageTestDetail(
                test_name=test_name,
                avg_price=avg_price,
                cheapest_price=round(cheapest[0], 2),
                cheapest_provider=cheapest[1],
            )
        )

        total_cost += cheapest[0]
        market_avg_total += avg_price

    total_cost = round(total_cost, 2)
    market_avg_total = round(market_avg_total, 2)

    # Apply margin
    if request.margin >= 100:
        raise ValueError("Margin cannot be 100% or higher")

    suggested_price = round(total_cost / (1 - request.margin / 100), 2) if total_cost > 0 else 0.0
    expected_profit = round(suggested_price - total_cost, 2)

    return CustomPackageResponse(
        tests=test_details,
        total_cost=total_cost,
        margin_percent=request.margin,
        suggested_package_price=suggested_price,
        expected_profit=expected_profit,
        market_average_total=market_avg_total if market_avg_total > 0 else None,
    )
