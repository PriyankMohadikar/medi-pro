"""
Comparison API Router

API 5: POST /compare/tests    → Compare test prices across providers
API 6: POST /compare/packages → Compare package prices across providers
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.schemas import (
    CompareTestsRequest,
    CompareTestsResponse,
    ComparePackagesRequest,
    ComparePackagesResponse,
)
from app.services.comparison_service import compare_test_prices, compare_package_prices

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/compare", tags=["Comparison"])


@router.post(
    "/tests",
    response_model=CompareTestsResponse,
    summary="Compare test prices across providers",
)
def compare_tests(
    request: CompareTestsRequest,
    db: Session = Depends(get_db),
):
    """
    API 5: Compare prices for multiple tests across all providers.

    Input:
      - tests: List of test names (e.g., ["CBC", "HbA1c", "Vitamin D"])
      - city: Optional city filter (e.g., "Ahmedabad")

    Returns each provider's individual prices, total, lowest, highest, and market average.
    """
    logger.info(f"POST /compare/tests — tests={request.tests}, city={request.city}")

    result = compare_test_prices(db, request.tests, request.city)

    if not result.providers:
        raise HTTPException(
            status_code=404,
            detail=f"No providers found offering the requested tests"
            + (f" in '{request.city}'" if request.city else "")
            + ".",
        )

    return result


@router.post(
    "/packages",
    response_model=ComparePackagesResponse,
    summary="Compare package prices across providers",
)
def compare_packages(
    request: ComparePackagesRequest,
    db: Session = Depends(get_db),
):
    """
    API 6: Compare a single package across all providers.

    Input:
      - package_name: Name of the package
      - city: Optional city filter

    Returns all providers, package prices, lowest, highest, and average.
    """
    logger.info(
        f"POST /compare/packages — package={request.package_name}, city={request.city}"
    )

    result = compare_package_prices(db, request.package_name, request.city)

    if not result.providers:
        raise HTTPException(
            status_code=404,
            detail=f"Package '{request.package_name}' not found"
            + (f" in '{request.city}'" if request.city else "")
            + ".",
        )

    return result
