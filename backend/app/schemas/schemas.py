"""
Pydantic schemas for request validation and response serialization.

All schemas use Pydantic V2 model_config for ORM compatibility.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ────────────────────────────────────────────────────────────
# Provider Schemas
# ────────────────────────────────────────────────────────────

class ProviderResponse(BaseModel):
    provider_id: int
    provider_name: str
    provider_type: Optional[str] = None
    city: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ────────────────────────────────────────────────────────────
# Test Schemas
# ────────────────────────────────────────────────────────────

class TestResponse(BaseModel):
    pricing_id: int
    test_name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    provider_name: Optional[str] = None
    provider_type: Optional[str] = None
    city: Optional[str] = None

    model_config = {"from_attributes": True}


class TestByNameResponse(BaseModel):
    """Response for GET /tests/{test_name} — one entry per provider offering the test."""
    provider_name: str
    price: Optional[float] = None
    city: Optional[str] = None
    category: Optional[str] = None

    model_config = {"from_attributes": True}


# ────────────────────────────────────────────────────────────
# Package Schemas
# ────────────────────────────────────────────────────────────

class PackageResponse(BaseModel):
    package_id: int
    package_name: Optional[str] = None
    package_price: Optional[float] = None
    provider_name: Optional[str] = None
    city: Optional[str] = None
    tests_included: list[str] = []

    model_config = {"from_attributes": True}


class PackageDetailResponse(BaseModel):
    """Response for GET /packages/{package_name}."""
    package_name: str
    provider_name: str
    package_price: Optional[float] = None
    city: Optional[str] = None
    tests_included: list[str] = []

    model_config = {"from_attributes": True}


# ────────────────────────────────────────────────────────────
# Comparison Schemas
# ────────────────────────────────────────────────────────────

class CompareTestsRequest(BaseModel):
    """POST /compare/tests — request body."""
    tests: list[str] = Field(..., min_length=1, description="List of test names to compare")
    city: Optional[str] = Field(None, description="Filter by city (optional)")


class ProviderTestComparison(BaseModel):
    """One provider's prices for the requested tests."""
    provider_name: str
    city: Optional[str] = None
    prices: dict[str, Optional[float]] = {}
    total_price: float = 0.0


class CompareTestsResponse(BaseModel):
    """POST /compare/tests — response body."""
    tests_requested: list[str]
    city_filter: Optional[str] = None
    providers: list[ProviderTestComparison] = []
    lowest_total: Optional[float] = None
    lowest_provider: Optional[str] = None
    highest_total: Optional[float] = None
    highest_provider: Optional[str] = None
    average_market_price: Optional[float] = None


class ComparePackagesRequest(BaseModel):
    """POST /compare/packages — request body."""
    package_name: str = Field(..., description="Package name to compare")
    city: Optional[str] = Field(None, description="Filter by city (optional)")


class ProviderPackageComparison(BaseModel):
    provider_name: str
    city: Optional[str] = None
    package_price: Optional[float] = None
    tests_included: list[str] = []


class ComparePackagesResponse(BaseModel):
    """POST /compare/packages — response body."""
    package_name: str
    city_filter: Optional[str] = None
    providers: list[ProviderPackageComparison] = []
    lowest_price: Optional[float] = None
    lowest_provider: Optional[str] = None
    highest_price: Optional[float] = None
    highest_provider: Optional[str] = None
    average_price: Optional[float] = None


# ────────────────────────────────────────────────────────────
# Pricing / Margin Schemas
# ────────────────────────────────────────────────────────────

class MarginRequest(BaseModel):
    """POST /pricing/margin — request body."""
    price: float = Field(..., gt=0, description="Base price / cost")
    margin: float = Field(..., ge=0, le=100, description="Desired margin percentage")


class MarginResponse(BaseModel):
    """POST /pricing/margin — response body."""
    base_price: float
    margin_percent: float
    suggested_selling_price: float
    profit: float


class CustomPackageRequest(BaseModel):
    """POST /custom-package — request body."""
    tests: list[str] = Field(..., min_length=1, description="List of test names")
    city: Optional[str] = Field(None, description="Filter by city")
    margin: float = Field(default=20.0, ge=0, le=100, description="Desired margin %")


class CustomPackageTestDetail(BaseModel):
    test_name: str
    avg_price: Optional[float] = None
    cheapest_price: Optional[float] = None
    cheapest_provider: Optional[str] = None


class CustomPackageResponse(BaseModel):
    """POST /custom-package — response body."""
    tests: list[CustomPackageTestDetail]
    total_cost: float
    margin_percent: float
    suggested_package_price: float
    expected_profit: float
    market_average_total: Optional[float] = None


# ────────────────────────────────────────────────────────────
# Analytics Schemas
# ────────────────────────────────────────────────────────────

class MarketAnalyticsResponse(BaseModel):
    """GET /analytics/market — response body."""
    average_test_price: Optional[float] = None
    average_package_price: Optional[float] = None
    total_providers: int = 0
    total_packages: int = 0
    total_tests: int = 0
    total_unique_test_names: int = 0
    total_cities: int = 0
    cities: list[str] = []
    categories: list[str] = []


class ProviderRanking(BaseModel):
    provider_name: str
    city: Optional[str] = None
    average_test_price: Optional[float] = None
    total_tests_offered: int = 0


class CompetitorAnalyticsResponse(BaseModel):
    """GET /analytics/competitors — response body."""
    cheapest_provider: Optional[ProviderRanking] = None
    most_expensive_provider: Optional[ProviderRanking] = None
    provider_rankings: list[ProviderRanking] = []


# ────────────────────────────────────────────────────────────
# Dashboard Schema
# ────────────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    """GET /dashboard — aggregated summary."""
    total_providers: int = 0
    total_tests: int = 0
    total_packages: int = 0
    total_cities: int = 0
    average_test_price: Optional[float] = None
    average_package_price: Optional[float] = None
    categories: list[str] = []
    cities: list[str] = []
    cheapest_provider: Optional[str] = None
    most_expensive_provider: Optional[str] = None


# ────────────────────────────────────────────────────────────
# Chat Schema
# ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """POST /chat — request body."""
    question: str = Field(..., min_length=1, description="User question")


class ChatResponse(BaseModel):
    """POST /chat — response body."""
    question: str
    answer: str
    source: str = "placeholder"


# ────────────────────────────────────────────────────────────
# Stats Schema (matches frontend StatsData type)
# ────────────────────────────────────────────────────────────

class StatsResponse(BaseModel):
    """GET /api/stats — frontend dashboard KPI aggregates."""
    total_tests: int = 0
    total_providers: int = 0
    total_packages: int = 0
    average_price: float = 0.0
    cities: list[str] = []
    categories: list[str] = []
