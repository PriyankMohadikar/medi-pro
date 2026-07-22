"""
Dashboard API Router

API 12: GET /dashboard → Dashboard summary
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.schemas import DashboardResponse
from app.services.analytics_service import get_dashboard_summary

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Dashboard"])


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Dashboard summary",
)
def dashboard(db: Session = Depends(get_db)):
    """
    API 12: Return aggregated dashboard summary.

    Combines market analytics and competitor insights into a single response.
    """
    logger.info("GET /dashboard")
    return get_dashboard_summary(db)
