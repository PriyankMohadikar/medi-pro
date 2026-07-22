"""
Stats API Router

GET /stats → Return frontend dashboard KPI aggregates
             (total_tests, total_providers, total_packages, average_price, cities, categories)

This endpoint returns the exact shape the React frontend's StatsData type expects.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Provider, TestPricing, PackagePricing
from app.schemas.schemas import StatsResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Stats"])


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Frontend dashboard KPI stats",
)
def get_stats(db: Session = Depends(get_db)):
    """
    Return aggregated KPIs for the frontend dashboard.

    Matches the React frontend's StatsData interface:
      - total_tests, total_providers, total_packages
      - average_price (across all tests)
      - cities[] and categories[]
    """
    logger.info("GET /stats")

    # Total test pricing rows
    total_tests = db.query(func.count(TestPricing.pricing_id)).scalar() or 0

    # Total providers
    total_providers = db.query(func.count(Provider.provider_id)).scalar() or 0

    # Total packages
    total_packages = db.query(func.count(PackagePricing.package_id)).scalar() or 0

    # Average test price
    avg_price = (
        db.query(func.avg(TestPricing.price))
        .filter(TestPricing.price.isnot(None))
        .scalar()
    )

    # Distinct cities
    cities_result = (
        db.query(distinct(Provider.city))
        .filter(Provider.city.isnot(None))
        .order_by(Provider.city)
        .all()
    )
    cities = [c[0] for c in cities_result if c[0]]

    # Distinct categories
    categories_result = (
        db.query(distinct(TestPricing.category))
        .filter(TestPricing.category.isnot(None))
        .order_by(TestPricing.category)
        .all()
    )
    categories = [c[0] for c in categories_result if c[0]]

    return StatsResponse(
        total_tests=total_tests,
        total_providers=total_providers,
        total_packages=total_packages,
        average_price=round(float(avg_price), 2) if avg_price else 0.0,
        cities=cities,
        categories=categories,
    )
