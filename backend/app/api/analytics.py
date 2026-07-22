"""
Analytics API Router

API 10: GET /analytics/market      → Market analytics summary
API 11: GET /analytics/competitors → Competitor analytics and rankings
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.schemas import MarketAnalyticsResponse, CompetitorAnalyticsResponse
from app.services.analytics_service import get_market_average, get_competitor_analytics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/market",
    response_model=MarketAnalyticsResponse,
    summary="Market analytics summary",
)
def market_analytics(db: Session = Depends(get_db)):
    """
    API 10: Return aggregated market analytics.

    Includes average test price, average package price,
    total providers, total packages, total tests, cities, categories.
    """
    logger.info("GET /analytics/market")
    return get_market_average(db)


@router.get(
    "/competitors",
    response_model=CompetitorAnalyticsResponse,
    summary="Competitor analytics and rankings",
)
def competitor_analytics(db: Session = Depends(get_db)):
    """
    API 11: Return competitor analytics.

    Includes cheapest provider, most expensive provider,
    and full provider rankings sorted by average test price.
    """
    logger.info("GET /analytics/competitors")
    return get_competitor_analytics(db)
