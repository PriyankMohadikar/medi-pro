"""
Packages API Router

API 3: GET  /packages               → Return all packages
API 4: GET  /packages/{package_name} → Return package details by name
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.database.models import PackagePricing, Provider
from app.schemas.schemas import PackageResponse, PackageDetailResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/packages", tags=["Packages"])


@router.get("", response_model=list[PackageResponse], summary="Get all packages")
def get_all_packages(
    city: Optional[str] = Query(None, description="Filter by city"),
    db: Session = Depends(get_db),
):
    """
    API 3: Return all package pricing records with provider details and included tests.
    """
    logger.info(f"GET /packages — city={city}")

    query = db.query(PackagePricing).join(
        Provider, PackagePricing.provider_id == Provider.provider_id
    )

    if city:
        query = query.filter(func.lower(Provider.city) == city.lower())

    packages = query.order_by(PackagePricing.package_name).all()

    return [
        PackageResponse(
            package_id=pkg.package_id,
            package_name=pkg.package_name,
            package_price=float(pkg.package_price) if pkg.package_price else None,
            provider_name=pkg.provider.provider_name if pkg.provider else None,
            city=pkg.provider.city if pkg.provider else None,
            tests_included=[t.test_name for t in pkg.tests if t.test_name],
        )
        for pkg in packages
    ]


@router.get(
    "/{package_name}",
    response_model=list[PackageDetailResponse],
    summary="Get package by name",
)
def get_package_by_name(
    package_name: str,
    city: Optional[str] = Query(None, description="Filter by city"),
    db: Session = Depends(get_db),
):
    """
    API 4: Return all providers offering a specific package.
    Includes package name, provider, price, city, and included tests.
    """
    logger.info(f"GET /packages/{package_name} — city={city}")

    query = (
        db.query(PackagePricing)
        .join(Provider, PackagePricing.provider_id == Provider.provider_id)
        .filter(func.lower(PackagePricing.package_name) == package_name.lower())
    )

    if city:
        query = query.filter(func.lower(Provider.city) == city.lower())

    packages = query.all()

    if not packages:
        raise HTTPException(
            status_code=404,
            detail=f"Package '{package_name}' not found in the database.",
        )

    return [
        PackageDetailResponse(
            package_name=pkg.package_name,
            provider_name=pkg.provider.provider_name if pkg.provider else "Unknown",
            package_price=float(pkg.package_price) if pkg.package_price else None,
            city=pkg.provider.city if pkg.provider else None,
            tests_included=[t.test_name for t in pkg.tests if t.test_name],
        )
        for pkg in packages
    ]
