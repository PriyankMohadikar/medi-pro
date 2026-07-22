"""
Pricing API Router

API 7: POST /pricing/margin  → Calculate margin and suggested selling price
API 8: POST /custom-package  → Build a custom package with margin
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.schemas import (
    MarginRequest,
    MarginResponse,
    CustomPackageRequest,
    CustomPackageResponse,
)
from app.services.pricing_service import calculate_margin
from app.services.package_service import build_custom_package

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Pricing"])


@router.post(
    "/pricing/margin",
    response_model=MarginResponse,
    summary="Calculate pricing margin",
)
def pricing_margin(request: MarginRequest):
    """
    API 7: Calculate suggested selling price and profit from cost + margin %.

    Input:
      - price: Base price / cost (e.g., 2500)
      - margin: Desired margin percentage (e.g., 20)

    Returns suggested selling price, profit, and margin.
    """
    logger.info(f"POST /pricing/margin — price={request.price}, margin={request.margin}")

    try:
        return calculate_margin(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/custom-package",
    response_model=CustomPackageResponse,
    summary="Build custom package",
)
def custom_package(
    request: CustomPackageRequest,
    db: Session = Depends(get_db),
):
    """
    API 8: Build a custom package from a list of tests.

    Input:
      - tests: List of test names (e.g., ["CBC", "HbA1c", "Lipid", "Vitamin D"])
      - city: Optional city filter (e.g., "Ahmedabad")
      - margin: Desired margin % (default: 20)

    Returns individual prices, total cost, suggested package price,
    expected profit, and market average.
    """
    logger.info(
        f"POST /custom-package — tests={request.tests}, city={request.city}, margin={request.margin}"
    )

    try:
        result = build_custom_package(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result
