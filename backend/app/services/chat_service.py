"""
Chat Service — Placeholder for AI integration (Stage 3).

This module exposes Python functions that will later be
registered as tools/functions for the AI to call.

Currently returns placeholder responses.

Functions exposed for AI tool-calling:
  - compare_test_prices()
  - calculate_margin()
  - build_custom_package()
  - get_market_analytics()
  - get_provider_rankings()
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.services.comparison_service import compare_test_prices, compare_package_prices
from app.services.pricing_service import calculate_margin
from app.services.package_service import build_custom_package
from app.services.analytics_service import (
    get_market_average,
    get_competitor_analytics,
    get_dashboard_summary,
)
from app.schemas.schemas import (
    MarginRequest,
    CustomPackageRequest,
    ChatRequest,
    ChatResponse,
)

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────
# Functions that will be exposed to the AI as tools
# ────────────────────────────────────────────────────────────

def chat_compare_test_prices(
    db: Session,
    test_names: list[str],
    city: Optional[str] = None,
) -> dict:
    """
    Compare test prices — callable by the AI.
    Returns a dictionary suitable for JSON serialization.
    """
    result = compare_test_prices(db, test_names, city)
    return result.model_dump()


def chat_calculate_margin(price: float, margin: float) -> dict:
    """
    Calculate margin — callable by the AI.
    """
    request = MarginRequest(price=price, margin=margin)
    result = calculate_margin(request)
    return result.model_dump()


def chat_build_custom_package(
    db: Session,
    test_names: list[str],
    city: Optional[str] = None,
    margin: float = 20.0,
) -> dict:
    """
    Build custom package — callable by the AI.
    """
    request = CustomPackageRequest(tests=test_names, city=city, margin=margin)
    result = build_custom_package(db, request)
    return result.model_dump()


def chat_get_market_analytics(db: Session) -> dict:
    """
    Get market analytics — callable by the AI.
    """
    result = get_market_average(db)
    return result.model_dump()


def chat_get_provider_rankings(db: Session) -> dict:
    """
    Get competitor analytics — callable by the AI.
    """
    result = get_competitor_analytics(db)
    return result.model_dump()


# ────────────────────────────────────────────────────────────
# Chat endpoint handler (placeholder)
# ────────────────────────────────────────────────────────────

def handle_chat(db: Session, request: ChatRequest) -> ChatResponse:
    """
    Handle a chat request.

    Currently returns a placeholder response.
    In Stage 3, this will:
      1. Send the user question to the AI provider
      2. The AI will decide which tool/function to call
      3. Execute the function against PostgreSQL
      4. Return the result to the user via the AI's response
    """
    logger.info(f"Chat request received: {request.question}")

    return ChatResponse(
        question=request.question,
        answer="Chat service ready. AI integration pending.",
        source="placeholder",
    )
