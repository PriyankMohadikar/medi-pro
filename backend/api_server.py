"""
FastAPI API Server for MediPrice Pro.

Serves REST endpoints that query the PostgreSQL healthcare_pricing database
using the existing SQLAlchemy models, config, and database modules.

Run:
    python api_server.py
    → http://localhost:8000

Endpoints:
    GET /api/health     — DB connectivity check
    GET /api/providers  — All providers (filter: ?city=)
    GET /api/tests      — Test pricing with provider info (filter: ?city=, ?provider=, ?category=)
    GET /api/packages   — Packages with included tests (filter: ?city=, ?provider=)
    GET /api/stats      — Dashboard KPI aggregates
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from config import load_settings
from database import get_engine, get_session_factory, create_tables
from models import PackagePricing, PackageTest, Provider, TestPricing
from ollama_utils import ensure_ollama_ready, check_ollama_status, is_model_available
import time

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("api_server")

# Global DB references (set during lifespan startup)
# ---------------------------------------------------------------------------
SessionFactory = None
settings = load_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Connects to PostgreSQL on startup using existing config/database modules.
    """
    global SessionFactory

    logger.info("Starting MediPrice Pro API server...")
    settings = load_settings()
    engine = get_engine(settings)
    SessionFactory = get_session_factory(engine)
    logger.info(
        f"Connected to PostgreSQL: {settings.DB_NAME} "
        f"@ {settings.DB_HOST}:{settings.DB_PORT}"
    )

    # Ensure all tables exist (including custom_packages, custom_package_tests)
    create_tables(engine)
    logger.info("Database tables verified/created")

    logger.info("Checking Ollama status...")
    ollama_status = await ensure_ollama_ready()
    if ollama_status["running"] and ollama_status["model_loaded"]:
        logger.info("Ollama Connected")
        logger.info("Model Ready")
    else:
        logger.warning(f"Ollama check issue: {ollama_status['message']}")
        
    logger.info("Application Ready")

    yield  # app runs

    logger.info("Shutting down API server...")
    engine.dispose()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="MediPrice Pro API",
    description="Healthcare pricing intelligence REST API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev servers & configured production origins
default_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
custom_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
allowed_origins = list(set(default_origins + custom_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from chat_router import router as chat_router
app.include_router(chat_router)

from custom_packages_router import router as custom_packages_router
app.include_router(custom_packages_router)

from analyzed_tests_router import router as analyzed_tests_router
app.include_router(analyzed_tests_router)

def get_db() -> Session:
    """Create a new DB session. Caller must close it."""
    if SessionFactory is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    return SessionFactory()


# =========================================================================
# GET /api/health
# =========================================================================
@app.get("/api/health")
async def health_check():
    """Database connectivity check with row counts."""
    session = get_db()
    try:
        test_count = session.query(func.count(TestPricing.pricing_id)).scalar()
        provider_count = session.query(func.count(Provider.provider_id)).scalar()
        package_count = session.query(func.count(PackagePricing.package_id)).scalar()

        start_time = time.time()
        
        # Check ollama asynchronously
        ollama_running = await check_ollama_status()
        model_loaded = await is_model_available(settings.OLLAMA_MODEL) if ollama_running else False
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "ok",
            "database": "connected",
            "ollama": "Running" if ollama_running else "Not Running",
            "model_loaded": model_loaded,
            "response_time_ms": response_time,
            "rows": {
                "providers": provider_count,
                "test_pricing": test_count,
                "package_pricing": package_count,
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
    finally:
        session.close()


# =========================================================================
# GET /api/providers
# =========================================================================
@app.get("/api/providers")
def get_providers(
    city: Optional[str] = Query(None, description="Filter by city"),
):
    """Return all providers, optionally filtered by city."""
    session = get_db()
    try:
        query = session.query(Provider).order_by(Provider.provider_name)

        if city:
            query = query.filter(Provider.city.ilike(f"%{city}%"))

        providers = query.all()
        return [
            {
                "provider_id": p.provider_id,
                "provider_name": p.provider_name,
                "provider_type": p.provider_type,
                "city": p.city,
            }
            for p in providers
        ]
    except Exception as e:
        logger.error(f"Error fetching providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch providers")
    finally:
        session.close()


# =========================================================================
# GET /api/tests
# =========================================================================
@app.get("/api/tests")
def get_tests(
    city: Optional[str] = Query(None, description="Filter by city"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    category: Optional[str] = Query(None, description="Filter by test category"),
):
    """
    Return test pricing joined with provider details.
    Supports optional filters for city, provider, and category.
    """
    session = get_db()
    try:
        query = (
            session.query(TestPricing, Provider)
            .join(Provider, TestPricing.provider_id == Provider.provider_id)
            .order_by(TestPricing.test_name, Provider.provider_name)
        )

        if city:
            query = query.filter(Provider.city.ilike(f"%{city}%"))
        if provider:
            query = query.filter(Provider.provider_name.ilike(f"%{provider}%"))
        if category:
            query = query.filter(TestPricing.category.ilike(f"%{category}%"))

        results = query.all()
        return [
            {
                "pricing_id": tp.pricing_id,
                "test_name": tp.test_name,
                "category": tp.category,
                "price": float(tp.price) if tp.price is not None else None,
                "provider_name": prov.provider_name,
                "provider_type": prov.provider_type,
                "city": prov.city,
            }
            for tp, prov in results
        ]
    except Exception as e:
        logger.error(f"Error fetching tests: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch test pricing")
    finally:
        session.close()


# Pydantic Schemas for CRUD
from pydantic import BaseModel

class TestPricingCreate(BaseModel):
    test_name: str
    category: Optional[str] = None
    price: float
    provider_id: Optional[int] = None
    provider_name: Optional[str] = None
    city: Optional[str] = None

class TestPricingUpdate(BaseModel):
    test_name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None

class ProviderCreate(BaseModel):
    provider_name: str
    provider_type: Optional[str] = None
    city: Optional[str] = None


# =========================================================================
# POST /api/tests — Create new test pricing record
# =========================================================================
@app.post("/api/tests", status_code=201)
def create_test(data: TestPricingCreate):
    session = get_db()
    try:
        provider_id = data.provider_id
        if not provider_id and data.provider_name and data.city:
            prov = session.query(Provider).filter(
                Provider.provider_name == data.provider_name,
                Provider.city == data.city
            ).first()
            if not prov:
                prov = Provider(provider_name=data.provider_name, city=data.city)
                session.add(prov)
                session.flush()
            provider_id = prov.provider_id

        new_test = TestPricing(
            provider_id=provider_id,
            test_name=data.test_name,
            category=data.category,
            price=data.price
        )
        session.add(new_test)
        session.commit()
        session.refresh(new_test)
        return {"pricing_id": new_test.pricing_id, "test_name": new_test.test_name, "price": float(new_test.price)}
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating test pricing: {e}")
        raise HTTPException(status_code=500, detail="Failed to create test pricing")
    finally:
        session.close()


# =========================================================================
# PUT /api/tests/{pricing_id} — Update existing test pricing
# =========================================================================
@app.put("/api/tests/{pricing_id}")
def update_test(pricing_id: int, data: TestPricingUpdate):
    session = get_db()
    try:
        tp = session.query(TestPricing).filter(TestPricing.pricing_id == pricing_id).first()
        if not tp:
            raise HTTPException(status_code=404, detail="Test pricing record not found")
        
        if data.test_name is not None:
            tp.test_name = data.test_name
        if data.category is not None:
            tp.category = data.category
        if data.price is not None:
            tp.price = data.price

        session.commit()
        return {"pricing_id": tp.pricing_id, "test_name": tp.test_name, "price": float(tp.price)}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating test pricing {pricing_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update test pricing")
    finally:
        session.close()


# =========================================================================
# DELETE /api/tests/{pricing_id} — Delete test pricing
# =========================================================================
@app.delete("/api/tests/{pricing_id}")
def delete_test(pricing_id: int):
    session = get_db()
    try:
        tp = session.query(TestPricing).filter(TestPricing.pricing_id == pricing_id).first()
        if not tp:
            raise HTTPException(status_code=404, detail="Test pricing record not found")
        
        session.delete(tp)
        session.commit()
        return {"detail": f"Test pricing record {pricing_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting test pricing {pricing_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete test pricing")
    finally:
        session.close()



# =========================================================================
# GET /api/packages
# =========================================================================
@app.get("/api/packages")
def get_packages(
    city: Optional[str] = Query(None, description="Filter by city"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
):
    """
    Return packages with nested included tests.
    Each package includes a list of test names from the package_tests table.
    """
    session = get_db()
    try:
        query = (
            session.query(PackagePricing, Provider)
            .join(Provider, PackagePricing.provider_id == Provider.provider_id)
            .order_by(PackagePricing.package_name)
        )

        if city:
            query = query.filter(Provider.city.ilike(f"%{city}%"))
        if provider:
            query = query.filter(Provider.provider_name.ilike(f"%{provider}%"))

        results = query.all()

        packages = []
        for pkg, prov in results:
            # Fetch included tests for this package
            tests = (
                session.query(PackageTest.test_name)
                .filter(PackageTest.package_id == pkg.package_id)
                .all()
            )
            tests_included = [t.test_name for t in tests if t.test_name]

            packages.append(
                {
                    "package_id": pkg.package_id,
                    "package_name": pkg.package_name,
                    "package_price": (
                        float(pkg.package_price)
                        if pkg.package_price is not None
                        else None
                    ),
                    "provider_name": prov.provider_name,
                    "provider_type": prov.provider_type,
                    "city": prov.city,
                    "tests_included": tests_included,
                }
            )

        return packages
    except Exception as e:
        logger.error(f"Error fetching packages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch packages")
    finally:
        session.close()


# =========================================================================
# GET /api/stats
# =========================================================================
@app.get("/api/stats")
def get_stats():
    """
    Return aggregated dashboard KPIs:
    total tests, providers, packages, average price, and list of cities.
    """
    session = get_db()
    try:
        total_tests = session.query(func.count(TestPricing.pricing_id)).scalar() or 0
        total_providers = (
            session.query(func.count(Provider.provider_id)).scalar() or 0
        )
        total_packages = (
            session.query(func.count(PackagePricing.package_id)).scalar() or 0
        )
        avg_price = (
            session.query(func.avg(TestPricing.price))
            .filter(TestPricing.price.isnot(None))
            .scalar()
        )
        cities = (
            session.query(Provider.city)
            .filter(Provider.city.isnot(None))
            .distinct()
            .order_by(Provider.city)
            .all()
        )
        categories = (
            session.query(TestPricing.category)
            .filter(TestPricing.category.isnot(None))
            .distinct()
            .order_by(TestPricing.category)
            .all()
        )
        test_names = (
            session.query(TestPricing.test_name)
            .filter(TestPricing.test_name.isnot(None))
            .distinct()
            .order_by(TestPricing.test_name)
            .all()
        )

        return {
            "total_tests": total_tests,
            "total_providers": total_providers,
            "total_packages": total_packages,
            "average_price": round(float(avg_price), 2) if avg_price else 0,
            "cities": [c[0] for c in cities],
            "categories": [c[0] for c in categories],
            "test_names": [t[0] for t in test_names],
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stats")
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
