"""
Pricing Service — Business logic for margin calculation.

Functions:
  - calculate_margin() → Compute suggested selling price and profit from cost + margin %
"""

import logging

from app.schemas.schemas import MarginRequest, MarginResponse

logger = logging.getLogger(__name__)


def calculate_margin(request: MarginRequest) -> MarginResponse:
    """
    Given a base price and desired margin percentage,
    calculate the suggested selling price and expected profit.

    Formula:
      selling_price = price / (1 - margin/100)
      profit = selling_price - price
    """
    logger.info(f"Calculating margin: price={request.price}, margin={request.margin}%")

    if request.margin >= 100:
        # Prevent division by zero
        raise ValueError("Margin cannot be 100% or higher")

    selling_price = round(request.price / (1 - request.margin / 100), 2)
    profit = round(selling_price - request.price, 2)

    return MarginResponse(
        base_price=request.price,
        margin_percent=request.margin,
        suggested_selling_price=selling_price,
        profit=profit,
    )
