"""
MediPrice Pro — FastAPI Backend Application

Production-ready backend for the AI-powered Healthcare Pricing
Optimization & Competitive Intelligence System.

Features:
  - 13 REST APIs for tests, packages, comparison, pricing, analytics, stats
  - All routes served under /api prefix for frontend compatibility
  - Business logic isolated in service layer
  - Pydantic validation on all inputs/outputs
  - Auto-generated Swagger documentation at /docs
  - Prepared for Stage 3: Ollama AI integration via chat_service.py

Usage:
  cd backend
  python -m uvicorn app.main:app --reload --port 8000
"""

import logging
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database.database import test_connection
from app.api import tests as tests_router
from app.api import packages as packages_router
from app.api import comparison as comparison_router
from app.api import pricing as pricing_router
from app.api import providers as providers_router
from app.api import analytics as analytics_router
from app.api import dashboard as dashboard_router
from app.api import stats as stats_router

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chat_router import router as legacy_chat_router

# ────────────────────────────────────────────────────────────
# Logging Configuration
# ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/api.log", mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("mediprice")


# ────────────────────────────────────────────────────────────
# FastAPI Application
# ────────────────────────────────────────────────────────────

app = FastAPI(
    title="MediPrice Pro API",
    description=(
        "Production-ready REST API for Healthcare Pricing Optimization "
        "& Competitive Intelligence. Powered by PostgreSQL. "
        "All endpoints served under /api prefix. "
        "Prepared for Ollama AI integration (Stage 3)."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ────────────────────────────────────────────────────────────
# CORS Middleware
# ────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ────────────────────────────────────────────────────────────
# Global Exception Handler
# ────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# ────────────────────────────────────────────────────────────
# Register API Routers — All under /api prefix
# ────────────────────────────────────────────────────────────

app.include_router(tests_router.router, prefix="/api")
app.include_router(packages_router.router, prefix="/api")
app.include_router(comparison_router.router, prefix="/api")
app.include_router(pricing_router.router, prefix="/api")
app.include_router(providers_router.router, prefix="/api")
app.include_router(analytics_router.router, prefix="/api")
app.include_router(dashboard_router.router, prefix="/api")
app.include_router(stats_router.router, prefix="/api")
app.include_router(legacy_chat_router)


# ────────────────────────────────────────────────────────────
# Startup Event
# ────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Verify database connection on application startup."""
    logger.info("=" * 60)
    logger.info("MediPrice Pro API v2.0.0 — Starting up")
    logger.info("=" * 60)
    try:
        test_connection()
        logger.info("[OK] Database connection verified")
    except Exception as e:
        logger.error(f"[FAIL] Database connection failed: {e}")
        raise


# ────────────────────────────────────────────────────────────
# Health Check (root + /api/health)
# ────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health_check():
    """Root endpoint — API health check."""
    return {
        "status": "healthy",
        "application": "MediPrice Pro API",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/api/health", tags=["Health"])
def api_health():
    """Health endpoint for frontend monitoring."""
    return {"status": "ok"}

