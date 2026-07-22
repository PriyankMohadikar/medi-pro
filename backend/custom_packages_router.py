"""
Custom Packages CRUD Router.

Provides full CRUD operations for user-created custom healthcare packages.
All endpoints are prefixed with /api/custom-packages.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func

from models import CustomPackage, CustomPackageTest

logger = logging.getLogger("custom_packages_router")

router = APIRouter(prefix="/api/custom-packages", tags=["Custom Packages"])

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class TestIn(BaseModel):
    test_name: str
    individual_price: float | None = None
    display_order: int | None = None


class PackageIn(BaseModel):
    package_name: str = Field(..., min_length=1)
    total_tests: int | None = None
    individual_total_price: float | None = None
    discount_percentage: float | None = Field(None, ge=0)
    suggested_package_price: float | None = None
    market_average_price: float | None = None
    expected_customer_savings: float | None = None
    tests: list[TestIn] = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_session():
    """Get a DB session from the shared SessionFactory in api_server."""
    from api_server import get_db
    return get_db()


def _package_to_dict(pkg: CustomPackage) -> dict:
    """Serialize a CustomPackage ORM object to a dict."""
    return {
        "package_id": pkg.package_id,
        "package_name": pkg.package_name,
        "total_tests": pkg.total_tests,
        "individual_total_price": float(pkg.individual_total_price) if pkg.individual_total_price is not None else None,
        "discount_percentage": float(pkg.discount_percentage) if pkg.discount_percentage is not None else None,
        "suggested_package_price": float(pkg.suggested_package_price) if pkg.suggested_package_price is not None else None,
        "market_average_price": float(pkg.market_average_price) if pkg.market_average_price is not None else None,
        "expected_customer_savings": float(pkg.expected_customer_savings) if pkg.expected_customer_savings is not None else None,
        "created_at": pkg.created_at.isoformat() if pkg.created_at else None,
        "updated_at": pkg.updated_at.isoformat() if pkg.updated_at else None,
        "tests": [
            {
                "id": t.id,
                "test_name": t.test_name,
                "individual_price": float(t.individual_price) if t.individual_price is not None else None,
                "display_order": t.display_order,
            }
            for t in sorted(pkg.tests, key=lambda x: (x.display_order or 0))
        ],
    }


# =========================================================================
# GET /api/custom-packages — List all
# =========================================================================
@router.get("")
def list_custom_packages(
    search: Optional[str] = Query(None, description="Filter by package name"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="asc or desc"),
):
    """List all custom packages with optional search and sorting."""
    session = _get_session()
    try:
        query = session.query(CustomPackage)

        if search:
            query = query.filter(CustomPackage.package_name.ilike(f"%{search}%"))

        # Sorting
        sort_column_map = {
            "suggested_package_price": CustomPackage.suggested_package_price,
            "market_average_price": CustomPackage.market_average_price,
            "expected_customer_savings": CustomPackage.expected_customer_savings,
            "total_tests": CustomPackage.total_tests,
            "package_name": CustomPackage.package_name,
            "created_at": CustomPackage.created_at,
        }
        sort_col = sort_column_map.get(sort_by, CustomPackage.created_at)
        if sort_order == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        packages = query.all()
        return [_package_to_dict(p) for p in packages]
    except Exception as e:
        logger.error(f"Error listing custom packages: {e}")
        raise HTTPException(status_code=500, detail="Failed to list custom packages")
    finally:
        session.close()


# =========================================================================
# GET /api/custom-packages/{id} — Get single
# =========================================================================
@router.get("/{package_id}")
def get_custom_package(package_id: int):
    """Get a single custom package with its tests."""
    session = _get_session()
    try:
        pkg = session.query(CustomPackage).filter(
            CustomPackage.package_id == package_id
        ).first()
        if not pkg:
            raise HTTPException(status_code=404, detail="Package not found")
        return _package_to_dict(pkg)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching custom package {package_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch package")
    finally:
        session.close()


# =========================================================================
# POST /api/custom-packages — Create
# =========================================================================
@router.post("", status_code=201)
def create_custom_package(data: PackageIn):
    """Create a new custom package with tests."""
    session = _get_session()
    try:
        # Check for duplicate name
        existing = session.query(CustomPackage).filter(
            func.lower(CustomPackage.package_name) == data.package_name.strip().lower()
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"A package named '{data.package_name}' already exists"
            )

        pkg = CustomPackage(
            package_name=data.package_name.strip(),
            total_tests=data.total_tests or len(data.tests),
            individual_total_price=data.individual_total_price,
            discount_percentage=data.discount_percentage,
            suggested_package_price=data.suggested_package_price,
            market_average_price=data.market_average_price,
            expected_customer_savings=data.expected_customer_savings,
        )
        session.add(pkg)
        session.flush()  # get package_id

        for i, test in enumerate(data.tests):
            session.add(CustomPackageTest(
                package_id=pkg.package_id,
                test_name=test.test_name,
                individual_price=test.individual_price,
                display_order=test.display_order or i,
            ))

        session.commit()
        session.refresh(pkg)
        return _package_to_dict(pkg)

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating custom package: {e}")
        raise HTTPException(status_code=500, detail="Failed to create package")
    finally:
        session.close()


# =========================================================================
# PUT /api/custom-packages/{id} — Update
# =========================================================================
@router.put("/{package_id}")
def update_custom_package(package_id: int, data: PackageIn):
    """Update an existing custom package (replaces all tests)."""
    session = _get_session()
    try:
        pkg = session.query(CustomPackage).filter(
            CustomPackage.package_id == package_id
        ).first()
        if not pkg:
            raise HTTPException(status_code=404, detail="Package not found")

        # Check duplicate name (excluding self)
        existing = session.query(CustomPackage).filter(
            func.lower(CustomPackage.package_name) == data.package_name.strip().lower(),
            CustomPackage.package_id != package_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"A package named '{data.package_name}' already exists"
            )

        # Update fields
        pkg.package_name = data.package_name.strip()
        pkg.total_tests = data.total_tests or len(data.tests)
        pkg.individual_total_price = data.individual_total_price
        pkg.discount_percentage = data.discount_percentage
        pkg.suggested_package_price = data.suggested_package_price
        pkg.market_average_price = data.market_average_price
        pkg.expected_customer_savings = data.expected_customer_savings

        # Replace tests: delete old, insert new
        session.query(CustomPackageTest).filter(
            CustomPackageTest.package_id == package_id
        ).delete()

        for i, test in enumerate(data.tests):
            session.add(CustomPackageTest(
                package_id=package_id,
                test_name=test.test_name,
                individual_price=test.individual_price,
                display_order=test.display_order or i,
            ))

        session.commit()
        session.refresh(pkg)
        return _package_to_dict(pkg)

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating custom package {package_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update package")
    finally:
        session.close()


# =========================================================================
# POST /api/custom-packages/{id}/duplicate — Duplicate
# =========================================================================
@router.post("/{package_id}/duplicate", status_code=201)
def duplicate_custom_package(package_id: int):
    """Duplicate a package with '(Copy)' suffix."""
    session = _get_session()
    try:
        original = session.query(CustomPackage).filter(
            CustomPackage.package_id == package_id
        ).first()
        if not original:
            raise HTTPException(status_code=404, detail="Package not found")

        # Generate unique copy name
        base_name = f"{original.package_name} (Copy)"
        copy_name = base_name
        counter = 2
        while session.query(CustomPackage).filter(
            func.lower(CustomPackage.package_name) == copy_name.lower()
        ).first():
            copy_name = f"{base_name} {counter}"
            counter += 1

        new_pkg = CustomPackage(
            package_name=copy_name,
            total_tests=original.total_tests,
            individual_total_price=original.individual_total_price,
            discount_percentage=original.discount_percentage,
            suggested_package_price=original.suggested_package_price,
            market_average_price=original.market_average_price,
            expected_customer_savings=original.expected_customer_savings,
        )
        session.add(new_pkg)
        session.flush()

        for test in original.tests:
            session.add(CustomPackageTest(
                package_id=new_pkg.package_id,
                test_name=test.test_name,
                individual_price=test.individual_price,
                display_order=test.display_order,
            ))

        session.commit()
        session.refresh(new_pkg)
        return _package_to_dict(new_pkg)

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error duplicating custom package {package_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to duplicate package")
    finally:
        session.close()


# =========================================================================
# DELETE /api/custom-packages/{id} — Delete
# =========================================================================
@router.delete("/{package_id}")
def delete_custom_package(package_id: int):
    """Delete a custom package (cascades to tests)."""
    session = _get_session()
    try:
        pkg = session.query(CustomPackage).filter(
            CustomPackage.package_id == package_id
        ).first()
        if not pkg:
            raise HTTPException(status_code=404, detail="Package not found")

        session.delete(pkg)
        session.commit()
        return {"detail": "Package deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting custom package {package_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete package")
    finally:
        session.close()
