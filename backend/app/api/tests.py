"""
Tests API Router

API 1: GET  /tests             → Return all tests
API 2: GET  /tests/{test_name} → Return every provider offering the test
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.database.models import TestPricing, Provider
from app.schemas.schemas import TestResponse, TestByNameResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tests", tags=["Tests"])


@router.get("", response_model=list[TestResponse], summary="Get all tests")
def get_all_tests(
    category: Optional[str] = Query(None, description="Filter by category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    db: Session = Depends(get_db),
):
    """
    API 1: Return all test pricing records with provider details.
    Optionally filter by category or city.
    """
    logger.info(f"GET /tests — category={category}, city={city}")

    query = (
        db.query(
            TestPricing.pricing_id,
            TestPricing.test_name,
            TestPricing.category,
            TestPricing.price,
            Provider.provider_name,
            Provider.provider_type,
            Provider.city,
        )
        .join(Provider, TestPricing.provider_id == Provider.provider_id)
    )

    if category:
        query = query.filter(func.lower(TestPricing.category) == category.lower())
    if city:
        query = query.filter(func.lower(Provider.city) == city.lower())

    results = query.order_by(TestPricing.test_name, Provider.provider_name).all()

    return [
        TestResponse(
            pricing_id=r.pricing_id,
            test_name=r.test_name,
            category=r.category,
            price=float(r.price) if r.price is not None else None,
            provider_name=r.provider_name,
            provider_type=r.provider_type,
            city=r.city,
        )
        for r in results
    ]


@router.get("/{test_name}", response_model=list[TestByNameResponse], summary="Get test by name")
def get_test_by_name(
    test_name: str,
    city: Optional[str] = Query(None, description="Filter by city"),
    db: Session = Depends(get_db),
):
    """
    API 2: Return every provider offering a specific test.
    Includes provider name, price, city, and category.
    """
    logger.info(f"GET /tests/{test_name} — city={city}")

    query = (
        db.query(
            Provider.provider_name,
            TestPricing.price,
            Provider.city,
            TestPricing.category,
        )
        .join(Provider, TestPricing.provider_id == Provider.provider_id)
        .filter(func.lower(TestPricing.test_name) == test_name.lower())
    )

    if city:
        query = query.filter(func.lower(Provider.city) == city.lower())

    results = query.order_by(TestPricing.price.asc().nullslast()).all()

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Test '{test_name}' not found in the database.",
        )

    return [
        TestByNameResponse(
            provider_name=r.provider_name,
            price=float(r.price) if r.price is not None else None,
            city=r.city,
            category=r.category,
        )
        for r in results
    ]
