import json
from typing import Optional, List
from sqlalchemy import func, or_
from database import get_session_factory, get_engine
from config import load_settings
from models import PackagePricing, PackageTest, Provider, TestPricing, TestCost
from costing_helpers import (
    calculate_profit,
    calculate_profit_margin,
    calculate_markup,
    calculate_break_even_price,
    calculate_safe_discount,
    calculate_package_cost,
    calculate_package_profit,
    calculate_package_margin,
    suggest_optimal_price,
)

settings = load_settings()
engine = get_engine(settings)
SessionFactory = get_session_factory(engine)

def _resolve_canonical_test_name(session, test_name: str) -> Optional[str]:
    """Resolve a user/AI-provided test name to its exact canonical form in the database.
    Uses exact case-insensitive match first, then ILIKE fallback with shortest-name preference."""
    clean = test_name.strip().lower()
    # 1. Exact case-insensitive match
    exact = session.query(TestPricing.test_name).filter(
        func.lower(TestPricing.test_name) == clean
    ).first()
    if exact:
        return exact[0]
    # 2. ILIKE fallback — prefer the shortest (most specific) match
    fuzzy = session.query(TestPricing.test_name).filter(
        TestPricing.test_name.ilike(f"%{test_name.strip()}%")
    ).distinct().all()
    if fuzzy:
        names = [r[0] for r in fuzzy]
        names.sort(key=len)
        return names[0]
    return None


def _get_cost_for_test(session, test_name: str) -> Optional[float]:
    """Helper: fetch internal cost for a test name (exact match first, then fuzzy)."""
    clean = test_name.strip().lower()
    # Exact case-insensitive match first
    cost_row = session.query(TestCost).filter(
        func.lower(TestCost.test_name) == clean
    ).first()
    if not cost_row:
        # ILIKE fallback — prefer the shortest (most specific) match
        fuzzy = session.query(TestCost).filter(
            TestCost.test_name.ilike(f"%{test_name.strip()}%")
        ).all()
        if fuzzy:
            fuzzy.sort(key=lambda r: len(r.test_name))
            cost_row = fuzzy[0]
    if cost_row and cost_row.cost_price is not None:
        return float(cost_row.cost_price)
    return None


def _get_all_costs(session) -> dict:
    """Helper: fetch all test costs as {normalized_name: cost_price}."""
    costs = session.query(TestCost).all()
    return {c.test_name.strip().lower(): float(c.cost_price) for c in costs if c.cost_price is not None}


def get_market_average(test_name: str, city: Optional[str] = None) -> str:
    """
    Get the lowest, highest, and average market price for a specific test.
    Also includes internal cost and profitability data when available.
    
    Args:
        test_name: Name of the test (e.g., 'CBC', 'Vitamin D')
        city: Optional city to filter by.
    """
    session = SessionFactory()
    try:
        # Resolve to canonical DB test name (case-insensitive exact match first)
        canonical = _resolve_canonical_test_name(session, test_name)
        if not canonical:
            return json.dumps({"error": f"No pricing data found for {test_name}"})

        query = session.query(
            func.min(TestPricing.price).label("lowest"),
            func.max(TestPricing.price).label("highest"),
            func.avg(TestPricing.price).label("average")
        ).join(Provider, TestPricing.provider_id == Provider.provider_id)\
         .filter(func.lower(TestPricing.test_name) == canonical.lower())
         
        if city:
            query = query.filter(Provider.city.ilike(f"%{city}%"))
            
        result = query.first()
        
        if not result or result.average is None:
            return json.dumps({"error": f"No pricing data found for {test_name}"})

        response = {
            "test_name": canonical,
            "city": city or "All",
            "lowest_price": float(result.lowest),
            "highest_price": float(result.highest),
            "average_price": round(float(result.average), 2)
        }

        # Enrich with ES Healthcare price and internal cost
        es_row = session.query(TestPricing).join(Provider).filter(
            Provider.provider_name == "ES Healthcare",
            func.lower(TestPricing.test_name) == canonical.lower()
        ).first()
        if es_row and es_row.price is not None:
            es_price = float(es_row.price)
            response["es_price"] = es_price

            cost = _get_cost_for_test(session, canonical)
            if cost is not None:
                response["internal_cost"] = cost
                response["es_profit"] = calculate_profit(es_price, cost)
                response["es_margin_pct"] = calculate_profit_margin(es_price, cost)
                response["es_markup_pct"] = calculate_markup(es_price, cost)
                response["break_even_price"] = calculate_break_even_price(cost)

        return json.dumps(response)
    finally:
        session.close()

def compare_tests(test_names: List[str], city: Optional[str] = None) -> str:
    """
    Compare prices for a list of clinical tests across different providers.
    
    Args:
        test_names: List of test names to compare (e.g. ['CBC', 'HbA1c']).
        city: Optional city to filter by.
    """
    session = SessionFactory()
    try:
        results_list = []
        if not test_names:
            return json.dumps({"error": "No tests provided."})

        # Resolve each test name to canonical DB name
        resolved_names = []
        for t_name in test_names:
            canonical = _resolve_canonical_test_name(session, t_name)
            if canonical:
                resolved_names.append(canonical)
        if not resolved_names:
            return json.dumps({"error": "No pricing data found for the requested tests."})

        conditions = [func.lower(TestPricing.test_name) == name.lower() for name in resolved_names]
        query = session.query(TestPricing, Provider)\
            .join(Provider, TestPricing.provider_id == Provider.provider_id)\
            .filter(or_(*conditions))
            
        if city:
            query = query.filter(Provider.city.ilike(f"%{city}%"))
            
        test_results = query.all()
        for tp, prov in test_results:
            results_list.append({
                "test_name": tp.test_name,
                "provider": prov.provider_name,
                "city": prov.city,
                "price": float(tp.price) if tp.price else None
            })
                
        if not results_list:
            return json.dumps({"error": "No pricing data found for the requested tests."})
            
        return json.dumps({"test_comparisons": results_list})
    finally:
        session.close()

def compare_packages(package_names: List[str], city: Optional[str] = None) -> str:
    """
    Compare prices for health packages across different providers.
    
    Args:
        package_names: List of package names to compare (e.g. ['Diabetes Package', 'Executive Health']).
        city: Optional city to filter by.
    """
    session = SessionFactory()
    try:
        results_list = []
        if not package_names:
            return json.dumps({"error": "No packages provided."})
            
        conditions = [PackagePricing.package_name.ilike(f"%{p_name}%") for p_name in package_names]
        query = session.query(PackagePricing, Provider)\
            .join(Provider, PackagePricing.provider_id == Provider.provider_id)\
            .filter(or_(*conditions))
            
        if city:
            query = query.filter(Provider.city.ilike(f"%{city}%"))
            
        pkg_results = query.all()
        for pkg, prov in pkg_results:
            results_list.append({
                "package_name": pkg.package_name,
                "provider": prov.provider_name,
                "city": prov.city,
                "price": float(pkg.package_price) if pkg.package_price else None
            })
                
        if not results_list:
            return json.dumps({"error": "No package pricing found for the requested packages."})
            
        return json.dumps({"package_comparisons": results_list})
    finally:
        session.close()

def calculate_margin(cost: float, margin_percentage: float) -> str:
    """
    Calculate the required selling price to achieve a target true margin percentage.
    Formula: Selling Price = Cost / (1 - Margin/100)
    """
    if margin_percentage >= 100:
        return json.dumps({"error": "Margin percentage must be strictly less than 100%."})
        
    selling_price = cost / (1.0 - (margin_percentage / 100.0))
    profit = selling_price - cost
    
    return json.dumps({
        "base_cost": cost,
        "target_margin_percentage": margin_percentage,
        "required_selling_price": round(selling_price, 2),
        "expected_profit": round(profit, 2)
    })

def build_custom_package(tests: List[str], margin_percentage: float = 0.0) -> str:
    """
    Build a custom health package by aggregating the average market cost of individual tests, 
    then calculating the final package price using the requested margin.
    Also includes internal cost breakdown and profitability analysis.
    
    Args:
        tests: List of test names to include in the package.
        margin_percentage: The desired profit margin percentage (e.g., 20.0). Defaults to 0.0 if no margin requested.
    """
    session = SessionFactory()
    try:
        total_cost = 0.0
        test_details = []
        
        if not tests:
            return json.dumps({"error": "No tests provided."})

        # Resolve each test name to canonical DB name
        resolved_names = []
        for t_name in tests:
            canonical = _resolve_canonical_test_name(session, t_name)
            if canonical:
                resolved_names.append(canonical)
        if not resolved_names:
            return json.dumps({"error": "No pricing data found for the requested tests."})

        conditions = [func.lower(TestPricing.test_name) == name.lower() for name in resolved_names]
        results = session.query(TestPricing.test_name, func.avg(TestPricing.price).label('avg_price'))\
            .join(Provider, TestPricing.provider_id == Provider.provider_id)\
            .filter(Provider.provider_name == "ES Healthcare")\
            .filter(or_(*conditions))\
            .group_by(TestPricing.test_name).all()

        # Fetch all internal costs
        all_costs = _get_all_costs(session)
        total_internal_cost = 0.0
        has_cost_data = False

        for t_name, avg_price in results:
            avg_val = float(avg_price) if avg_price else 0.0
            total_cost += avg_val
            detail = {
                "test": t_name,
                "base_cost": round(avg_val, 2)
            }
            # Add internal cost if available
            cost_key = t_name.strip().lower()
            if cost_key in all_costs:
                internal_cost = all_costs[cost_key]
                detail["internal_cost"] = internal_cost
                detail["test_profit"] = calculate_profit(avg_val, internal_cost)
                detail["test_margin_pct"] = calculate_profit_margin(avg_val, internal_cost)
                total_internal_cost += internal_cost
                has_cost_data = True
            test_details.append(detail)
            
        profit = total_cost * (margin_percentage / 100.0)
        selling_price = total_cost + profit
        
        response = {
            "included_tests": test_details,
            "total_base_cost": round(total_cost, 2),
            "margin_percentage": margin_percentage,
            "profit": round(profit, 2),
            "suggested_package_price": round(selling_price, 2)
        }

        # Add package-level profitability if cost data exists
        if has_cost_data:
            response["total_internal_cost"] = round(total_internal_cost, 2)
            response["package_profit"] = calculate_package_profit(
                selling_price, [total_internal_cost]
            )
            response["package_margin_pct"] = calculate_package_margin(
                selling_price, [total_internal_cost]
            )

        return json.dumps(response)
    finally:
        session.close()

def get_pricing_analysis(status: Optional[str] = None, recommendation: Optional[str] = None, limit: int = 10) -> str:
    """
    Get a list of tests with their market pricing analysis (difference %, status, recommendation).
    Also includes internal cost and profitability data when available.
    Useful to answer "Which tests are overpriced?" or "Which tests should we reduce price on?"
    
    Args:
        status: Optional status filter (e.g., 'Overpriced', 'Underpriced', 'Competitive', 'Needs Review').
        recommendation: Optional recommendation filter (e.g., 'Reduce Price', 'Maintain Current Price', 'Price Leader', 'Monitor Competitors').
        limit: Max number of tests to return (default 10).
    """
    from analysis_logic import calculate_pricing_metrics
    session = SessionFactory()
    try:
        all_tests_query = session.query(TestPricing, Provider).join(Provider, TestPricing.provider_id == Provider.provider_id)
        all_results = all_tests_query.all()
        
        # Fetch all internal costs
        all_costs = _get_all_costs(session)
        
        # 1. Extract ES Healthcare baseline prices across all cities
        es_baseline_prices = {}
        for tp, prov in all_results:
            if prov.provider_name == "ES Healthcare" and tp.price:
                es_baseline_prices[tp.test_name] = float(tp.price)
                
        grouped_tests = {}
        for tp, prov in all_results:
            key = f"{tp.test_name}_{prov.city}"
            if key not in grouped_tests:
                grouped_tests[key] = {
                    "test_name": tp.test_name,
                    "city": prov.city,
                    "es_price": None,
                    "competitor_prices": []
                }
            if prov.provider_name == "ES Healthcare":
                grouped_tests[key]["es_price"] = float(tp.price) if tp.price else 0.0
            else:
                if tp.price:
                    grouped_tests[key]["competitor_prices"].append(float(tp.price))

        # Fallback missing es_prices to the baseline (so we can compare Gandhinagar competitors against ES Ahmedabad price)
        for key, data in grouped_tests.items():
            if data["es_price"] is None:
                data["es_price"] = es_baseline_prices.get(data["test_name"])

        results_list = []
        for key, data in grouped_tests.items():
            if data["es_price"] is None or not data["competitor_prices"]:
                continue
                
            metrics = calculate_pricing_metrics(data["es_price"], data["competitor_prices"])
            
            if status and metrics["status"].lower() != status.lower():
                continue
            if recommendation and metrics["recommendation"].lower() != recommendation.lower():
                continue
            
            entry = {
                "test_name": data["test_name"],
                "city": data["city"],
                "es_price": data["es_price"],
                "market_average": metrics["market_average"],
                "difference_pct": metrics["difference_pct"],
                "status": metrics["status"],
                "recommendation": metrics["recommendation"]
            }

            # Enrich with cost/profitability data
            cost_key = data["test_name"].strip().lower()
            if cost_key in all_costs:
                cost = all_costs[cost_key]
                es_price = data["es_price"]
                entry["cost_price"] = cost
                entry["profit"] = calculate_profit(es_price, cost)
                entry["margin_pct"] = calculate_profit_margin(es_price, cost)

            results_list.append(entry)
            
        # Sort by absolute difference percentage descending
        results_list.sort(key=lambda x: abs(x["difference_pct"]), reverse=True)
        results_list = results_list[:limit]
        
        if not results_list:
            return json.dumps({"message": "No tests found matching criteria."})
            
        return json.dumps({"analyzed_tests": results_list})
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# NEW PROFITABILITY TOOLS
# ═══════════════════════════════════════════════════════════════

def get_test_profitability(
    test_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    Get profitability data for ES Healthcare tests based on internal costs.
    Returns per-test: cost_price, es_price, profit, margin %, markup %,
    break-even price, max safe discount, and margin status.

    Args:
        test_name: Optional test name to look up (e.g. 'CBC'). If omitted, returns all.
        status: Optional filter: 'high_margin' (>40%), 'moderate' (20-40%),
                'low_margin' (<20%), 'loss_making' (<0%).
        limit: Max tests to return (default 10).
    """
    session = SessionFactory()
    try:
        # Get all ES Healthcare prices
        es_query = (
            session.query(TestPricing.test_name, TestPricing.price)
            .join(Provider, TestPricing.provider_id == Provider.provider_id)
            .filter(Provider.provider_name == "ES Healthcare")
            .filter(TestPricing.price.isnot(None))
        )
        if test_name:
            canonical = _resolve_canonical_test_name(session, test_name)
            if canonical:
                es_query = es_query.filter(func.lower(TestPricing.test_name) == canonical.lower())
            else:
                return json.dumps({"error": f"No ES Healthcare pricing data found for {test_name}"})

        es_results = es_query.all()
        if not es_results:
            return json.dumps({"error": f"No ES Healthcare pricing data found{' for ' + test_name if test_name else ''}"})

        # Get all costs
        all_costs = _get_all_costs(session)

        profitability_list = []
        for t_name, price in es_results:
            es_price = float(price)
            cost_key = t_name.strip().lower()
            cost = all_costs.get(cost_key)

            if cost is None:
                profitability_list.append({
                    "test_name": t_name,
                    "internal_cost": None,
                    "es_price": es_price,
                    "profit": None,
                    "margin_pct": None,
                    "markup_pct": None,
                    "break_even_price": None,
                    "max_safe_discount_pct": None,
                    "min_safe_price": None,
                    "margin_status": "Cost Data Missing",
                })
                continue

            margin_pct = calculate_profit_margin(es_price, cost)

            # Determine margin status
            if margin_pct < 0:
                margin_status = "Loss Making"
            elif margin_pct < 20:
                margin_status = "Low Margin"
            elif margin_pct <= 40:
                margin_status = "Moderate Margin"
            else:
                margin_status = "Healthy Margin"

            # Apply status filter
            if status:
                status_lower = status.lower().replace("_", " ")
                if status_lower == "high margin" and margin_pct <= 40:
                    continue
                elif status_lower == "moderate" and not (20 <= margin_pct <= 40):
                    continue
                elif status_lower == "low margin" and not (0 <= margin_pct < 20):
                    continue
                elif status_lower == "loss making" and margin_pct >= 0:
                    continue

            safe_discount = calculate_safe_discount(es_price, cost)

            profitability_list.append({
                "test_name": t_name,
                "internal_cost": cost,
                "es_price": es_price,
                "profit": calculate_profit(es_price, cost),
                "margin_pct": margin_pct,
                "markup_pct": calculate_markup(es_price, cost),
                "break_even_price": calculate_break_even_price(cost),
                "max_safe_discount_pct": safe_discount["max_discount_pct"],
                "min_safe_price": safe_discount["min_safe_price"],
                "margin_status": margin_status,
            })

        # Sort by margin descending (most profitable first)
        profitability_list.sort(key=lambda x: x["margin_pct"], reverse=True)
        profitability_list = profitability_list[:limit]

        if not profitability_list:
            return json.dumps({"message": "No profitability data found. Ensure internal costs are configured."})

        return json.dumps({"profitability_data": profitability_list})
    finally:
        session.close()


def get_discount_analysis(
    test_name: Optional[str] = None,
    discount_pct: Optional[float] = None,
) -> str:
    """
    Analyze whether a discount is safe for a test while maintaining profitability.
    Can also identify which tests can be safely discounted and which should never be.

    Args:
        test_name: Optional test name (e.g. 'CBC'). If omitted, analyzes all tests.
        discount_pct: Optional specific discount % to evaluate (e.g. 20.0 for 20% off).
    """
    session = SessionFactory()
    try:
        es_query = (
            session.query(TestPricing.test_name, TestPricing.price)
            .join(Provider, TestPricing.provider_id == Provider.provider_id)
            .filter(Provider.provider_name == "ES Healthcare")
            .filter(TestPricing.price.isnot(None))
        )
        if test_name:
            canonical = _resolve_canonical_test_name(session, test_name)
            if canonical:
                es_query = es_query.filter(func.lower(TestPricing.test_name) == canonical.lower())
            else:
                return json.dumps({"error": f"No pricing data found for {test_name}"})

        es_results = es_query.all()
        all_costs = _get_all_costs(session)

        analysis_list = []
        safe_to_discount = []
        never_discount = []

        for t_name, price in es_results:
            es_price = float(price)
            cost_key = t_name.strip().lower()
            cost = all_costs.get(cost_key)

            if cost is None:
                entry = {
                    "test_name": t_name,
                    "internal_cost": None,
                    "current_price": es_price,
                    "current_margin_pct": None,
                    "max_safe_discount_pct": None,
                    "min_safe_price": None,
                    "can_discount": None,
                }
                if discount_pct is not None:
                    discounted_price = round(es_price * (1 - discount_pct / 100), 2)
                    entry["requested_discount_pct"] = discount_pct
                    entry["discounted_price"] = discounted_price
                    entry["post_discount_margin_pct"] = None
                    entry["post_discount_profit"] = None
                    entry["is_discount_safe"] = "Cost Data Missing"
                analysis_list.append(entry)
                continue

            current_margin = calculate_profit_margin(es_price, cost)
            safe_info = calculate_safe_discount(es_price, cost)

            entry = {
                "test_name": t_name,
                "internal_cost": cost,
                "current_price": es_price,
                "current_margin_pct": current_margin,
                "max_safe_discount_pct": safe_info["max_discount_pct"],
                "min_safe_price": safe_info["min_safe_price"],
                "can_discount": safe_info["can_discount"],
            }

            # If a specific discount % was requested, simulate it
            if discount_pct is not None:
                discounted_price = round(es_price * (1 - discount_pct / 100), 2)
                post_discount_margin = calculate_profit_margin(discounted_price, cost)
                post_discount_profit = calculate_profit(discounted_price, cost)
                is_safe = post_discount_margin >= 20.0  # 20% minimum margin

                entry["requested_discount_pct"] = discount_pct
                entry["discounted_price"] = discounted_price
                entry["post_discount_margin_pct"] = post_discount_margin
                entry["post_discount_profit"] = post_discount_profit
                entry["is_discount_safe"] = is_safe

            analysis_list.append(entry)

            # Categorize
            if safe_info["max_discount_pct"] >= 10:
                safe_to_discount.append(t_name)
            elif current_margin < 25:
                never_discount.append(t_name)

        if not analysis_list:
            return json.dumps({"error": "No cost data available for discount analysis."})

        response = {"discount_analysis": analysis_list}
        if not test_name:  # Only include summaries for broad queries
            response["safe_to_discount"] = safe_to_discount
            response["never_discount"] = never_discount

        return json.dumps(response)
    finally:
        session.close()


def build_profitable_package(
    tests: List[str],
    target_margin_pct: float = 30.0,
    max_price: Optional[float] = None,
) -> str:
    """
    Build a health package with profitability analysis and targets.
    Calculates total internal cost, suggested price, expected profit,
    profit margin, and customer savings compared to individual prices.

    Args:
        tests: List of test names to include (e.g. ['CBC', 'Lipid Profile', 'TSH']).
        target_margin_pct: Desired profit margin percentage (default 30%).
        max_price: Optional maximum package price (e.g. 3000 for "under ₹3000").
    """
    session = SessionFactory()
    try:
        if not tests:
            return json.dumps({"error": "No tests provided."})

        all_costs = _get_all_costs(session)

        test_details = []
        total_internal_cost = 0.0
        total_es_price = 0.0
        missing_cost = []

        for t_name in tests:
            # Resolve to canonical DB name and get ES Healthcare price
            canonical = _resolve_canonical_test_name(session, t_name)
            es_row = None
            if canonical:
                es_row = (
                    session.query(TestPricing)
                    .join(Provider)
                    .filter(
                        Provider.provider_name == "ES Healthcare",
                        func.lower(TestPricing.test_name) == canonical.lower(),
                    )
                    .first()
                )

            es_price = float(es_row.price) if es_row and es_row.price else 0.0
            actual_name = es_row.test_name if es_row else t_name

            cost_key = actual_name.strip().lower()
            cost = all_costs.get(cost_key, None)

            detail = {
                "test": actual_name,
                "es_individual_price": es_price,
            }
            if cost is not None:
                detail["internal_cost"] = cost
                detail["individual_margin_pct"] = calculate_profit_margin(es_price, cost)
                total_internal_cost += cost
            else:
                missing_cost.append(actual_name)

            total_es_price += es_price
            test_details.append(detail)

        # Calculate package price for target margin
        if target_margin_pct >= 100:
            suggested_price = total_es_price  # Fallback
        else:
            suggested_price = round(
                total_internal_cost / (1 - target_margin_pct / 100), 0
            )

        # Apply max_price constraint if specified
        if max_price is not None and suggested_price > max_price:
            suggested_price = max_price

        package_profit = calculate_package_profit(suggested_price, [total_internal_cost])
        package_margin = calculate_package_margin(suggested_price, [total_internal_cost])
        customer_savings = round(total_es_price - suggested_price, 2)
        customer_savings_pct = (
            round((customer_savings / total_es_price) * 100, 1)
            if total_es_price > 0
            else 0.0
        )
        
        # Calculate what discount this represents on the total selling price
        implied_discount_pct = (
            round(((total_es_price - suggested_price) / total_es_price) * 100, 1)
            if total_es_price > 0 else 0.0
        )

        is_viable = package_margin >= 15.0  # Minimum 15% for viability

        response = {
            "included_tests": test_details,
            "total_individual_es_price": round(total_es_price, 2),
            "target_margin_pct": target_margin_pct,
            "suggested_package_price": suggested_price,
            "required_discount_on_es_price_pct": implied_discount_pct,
            "total_internal_cost": round(total_internal_cost, 2),
            "actual_margin_pct": package_margin,
            "expected_profit": package_profit,
            "customer_savings": customer_savings,
            "customer_savings_pct": customer_savings_pct,
            "is_financially_viable": is_viable,
        }

        if missing_cost:
            response["missing_cost_data"] = missing_cost

        return json.dumps(response)
    finally:
        session.close()
