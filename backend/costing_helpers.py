"""
Reusable costing helper functions for MediPrice Pro.

Pure calculation functions — no database access.
All functions take prices as arguments and return computed values.
Used by AI tools (chat_services.py) and any future profitability features.
"""

from typing import List, Dict, Any, Optional


def calculate_profit(selling_price: float, cost_price: float) -> float:
    """
    Calculate absolute profit per test.

    Args:
        selling_price: Current selling price (₹).
        cost_price: Internal processing cost (₹).

    Returns:
        Profit amount (₹). Negative means a loss.
    """
    return round(selling_price - cost_price, 2)


def calculate_profit_margin(selling_price: float, cost_price: float) -> float:
    """
    Calculate profit margin as a percentage of selling price.

    Formula: ((selling - cost) / selling) * 100

    Args:
        selling_price: Current selling price (₹).
        cost_price: Internal processing cost (₹).

    Returns:
        Profit margin percentage. Returns 0.0 if selling_price is zero.
    """
    if selling_price <= 0:
        return 0.0
    return round(((selling_price - cost_price) / selling_price) * 100, 1)


def calculate_markup(selling_price: float, cost_price: float) -> float:
    """
    Calculate markup as a percentage of cost.

    Formula: ((selling - cost) / cost) * 100

    Args:
        selling_price: Current selling price (₹).
        cost_price: Internal processing cost (₹).

    Returns:
        Markup percentage. Returns 0.0 if cost_price is zero.
    """
    if cost_price <= 0:
        return 0.0
    return round(((selling_price - cost_price) / cost_price) * 100, 1)


def calculate_break_even_price(cost_price: float) -> float:
    """
    Return the minimum selling price to avoid a loss.

    The break-even price equals the internal cost — selling at this
    price yields zero profit.

    Args:
        cost_price: Internal processing cost (₹).

    Returns:
        Break-even selling price (₹).
    """
    return round(cost_price, 2)


def calculate_safe_discount(
    selling_price: float,
    cost_price: float,
    min_margin_pct: float = 20.0,
) -> Dict[str, Any]:
    """
    Calculate the maximum safe discount that maintains a minimum profit margin.

    Args:
        selling_price: Current selling price (₹).
        cost_price: Internal processing cost (₹).
        min_margin_pct: Minimum acceptable profit margin % (default 20%).

    Returns:
        Dictionary with:
            - current_margin_pct: Current margin before any discount.
            - max_discount_pct: Maximum discount % that maintains min_margin_pct.
            - min_safe_price: Lowest acceptable selling price.
            - can_discount: Whether any discount is safe.
    """
    current_margin = calculate_profit_margin(selling_price, cost_price)

    # Minimum safe price = cost / (1 - min_margin_pct/100)
    if min_margin_pct >= 100:
        min_safe_price = float("inf")
    else:
        min_safe_price = round(cost_price / (1 - min_margin_pct / 100), 2)

    if selling_price <= 0:
        return {
            "current_margin_pct": 0.0,
            "max_discount_pct": 0.0,
            "min_safe_price": min_safe_price,
            "can_discount": False,
        }

    max_discount_pct = round(
        ((selling_price - min_safe_price) / selling_price) * 100, 1
    )
    max_discount_pct = max(0.0, max_discount_pct)

    return {
        "current_margin_pct": current_margin,
        "max_discount_pct": max_discount_pct,
        "min_safe_price": min_safe_price,
        "can_discount": max_discount_pct > 0,
    }


def calculate_package_cost(test_costs: List[float]) -> float:
    """
    Calculate total internal cost for a package of tests.

    Args:
        test_costs: List of individual test cost prices (₹).

    Returns:
        Total package cost (₹).
    """
    return round(sum(test_costs), 2)


def calculate_package_profit(
    package_price: float, test_costs: List[float]
) -> float:
    """
    Calculate profit from a package.

    Args:
        package_price: Package selling price (₹).
        test_costs: List of individual test cost prices (₹).

    Returns:
        Package profit (₹).
    """
    total_cost = calculate_package_cost(test_costs)
    return round(package_price - total_cost, 2)


def calculate_package_margin(
    package_price: float, test_costs: List[float]
) -> float:
    """
    Calculate profit margin for a package.

    Args:
        package_price: Package selling price (₹).
        test_costs: List of individual test cost prices (₹).

    Returns:
        Package profit margin percentage.
    """
    if package_price <= 0:
        return 0.0
    total_cost = calculate_package_cost(test_costs)
    return round(((package_price - total_cost) / package_price) * 100, 1)


def suggest_optimal_price(
    cost_price: float,
    competitor_prices: List[float],
    market_average: float,
    target_margin_pct: float = 30.0,
) -> Dict[str, Any]:
    """
    Suggest an optimal selling price considering cost, competition, and margin.

    The algorithm:
    1. Calculate the minimum price for the target margin.
    2. Compare against market average and competitor range.
    3. Suggest a price that balances profitability and competitiveness.

    Args:
        cost_price: Internal processing cost (₹).
        competitor_prices: List of competitor selling prices (₹).
        market_average: Current market average price (₹).
        target_margin_pct: Desired profit margin % (default 30%).

    Returns:
        Dictionary with:
            - suggested_price: Recommended selling price.
            - expected_margin_pct: Margin at the suggested price.
            - expected_profit: Profit at the suggested price.
            - vs_market_pct: How the suggestion compares to market average.
            - price_range_low: Conservative lower bound.
            - price_range_high: Aggressive upper bound.
            - reasoning: Brief explanation of the recommendation.
    """
    # Minimum price for target margin
    if target_margin_pct >= 100:
        min_target_price = float("inf")
    else:
        min_target_price = cost_price / (1 - target_margin_pct / 100)

    lowest_competitor = min(competitor_prices) if competitor_prices else market_average
    highest_competitor = max(competitor_prices) if competitor_prices else market_average

    # Strategy: suggest price near market average but ensure target margin
    if min_target_price <= market_average:
        # We can be competitive AND profitable — aim slightly below market
        suggested = round(market_average * 0.95, 0)  # 5% below market
        if suggested < min_target_price:
            suggested = round(min_target_price, 0)
        reasoning = (
            "The suggested price is slightly below market average, "
            "maintaining strong competitiveness while exceeding the target profit margin."
        )
    elif min_target_price <= highest_competitor:
        # We need to price above average but within competitor range
        suggested = round(min_target_price * 1.05, 0)  # 5% above minimum
        reasoning = (
            "To achieve the target margin, the price needs to be above market average "
            "but remains within the competitor price range, keeping it justifiable."
        )
    else:
        # Target margin requires pricing above all competitors — flag this
        suggested = round(min_target_price * 1.05, 0)
        reasoning = (
            "Achieving the target margin requires pricing above the competitor range. "
            "Consider whether the target margin is realistic, or if operational cost "
            "reduction could improve the margin at a lower price point."
        )

    expected_margin = calculate_profit_margin(suggested, cost_price)
    expected_profit = calculate_profit(suggested, cost_price)
    vs_market = round(((suggested - market_average) / market_average) * 100, 1) if market_average > 0 else 0.0

    # Price range: conservative (near break-even + small margin) to aggressive (above market)
    price_range_low = round(cost_price / (1 - 15 / 100), 0)   # 15% margin floor
    price_range_high = round(market_average * 1.10, 0)          # 10% above market ceiling
    if price_range_high < min_target_price:
        price_range_high = round(min_target_price * 1.10, 0)

    return {
        "suggested_price": suggested,
        "expected_margin_pct": expected_margin,
        "expected_profit": expected_profit,
        "vs_market_pct": vs_market,
        "price_range_low": price_range_low,
        "price_range_high": price_range_high,
        "reasoning": reasoning,
    }
