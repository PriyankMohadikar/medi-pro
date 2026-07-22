from typing import Dict, Any, List

def calculate_pricing_metrics(es_price: float, competitor_prices: List[float]) -> Dict[str, Any]:
    """Calculates lowest, highest, average, difference %, status, and recommendation."""
    if not competitor_prices:
        return {
            "lowest_price": 0,
            "highest_price": 0,
            "market_average": 0,
            "difference_pct": 0,
            "status": "Competitive",
            "recommendation": "Maintain Current Price"
        }

    lowest = min(competitor_prices)
    highest = max(competitor_prices)
    avg = sum(competitor_prices) / len(competitor_prices)
    diff_pct = ((es_price - avg) / avg) * 100 if avg > 0 else 0

    status = "Competitive"
    recommendation = "Maintain Current Price"

    if diff_pct > 25:
        status = "Overpriced"
        recommendation = "Review Immediately"
    elif diff_pct > 15:
        status = "Overpriced"
        recommendation = "Reduce Price"
    elif diff_pct > 5:
        status = "Needs Review"
        recommendation = "Monitor Competitors"
    elif diff_pct < -20:
        status = "Underpriced"
        if es_price < lowest:
            recommendation = "Price Leader"
        else:
            recommendation = "Increase Price"
    elif diff_pct < -5:
        status = "Competitive"
        recommendation = "Highly Competitive"
    else:
        status = "Competitive"
        recommendation = "Maintain Current Price"

    return {
        "lowest_price": float(lowest),
        "highest_price": float(highest),
        "market_average": float(avg),
        "difference_pct": round(diff_pct, 1),
        "status": status,
        "recommendation": recommendation
    }
