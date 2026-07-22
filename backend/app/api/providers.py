"""
Providers API Router

API 9: GET /providers → Return all healthcare providers
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.database.models import Provider
from app.schemas.schemas import ProviderResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("", response_model=list[ProviderResponse], summary="Get all providers")
def get_all_providers(
    city: Optional[str] = Query(None, description="Filter by city"),
    provider_type: Optional[str] = Query(None, description="Filter by provider type"),
    db: Session = Depends(get_db),
):
    """
    API 9: Return all healthcare providers.
    Optionally filter by city or provider type.
    """
    logger.info(f"GET /providers — city={city}, type={provider_type}")

    query = db.query(Provider)

    if city:
        query = query.filter(func.lower(Provider.city) == city.lower())
    if provider_type:
        query = query.filter(func.lower(Provider.provider_type) == provider_type.lower())

    providers = query.order_by(Provider.provider_name).all()

    return [ProviderResponse.model_validate(p) for p in providers]
