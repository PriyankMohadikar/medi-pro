import json
from typing import Optional, List
from sqlalchemy import func, or_
from database import get_session_factory, get_engine
from config import load_settings
from models import PackagePricing, PackageTest, Provider, TestPricing

settings = load_settings()
engine = get_engine(settings)
SessionFactory = get_session_factory(engine)

def get_market_average(test_name: str, city: Optional[str] = None) -> str:
    """
    Get the lowest, highest, and average market price for a specific test.
    
    Args:
        test_name: Name of the test (e.g., 'CBC', 'Vitamin D')
        city: Optional city to filter by.
    """
    session = SessionFactory()
    try:
        query = session.query(
            func.min(TestPricing.price).label("lowest"),
            func.max(TestPricing.price).label("highest"),
            func.avg(TestPricing.price).label("average")
        ).join(Provider, TestPricing.provider_id == Provider.provider_id)\
         .filter(TestPricing.test_name.ilike(f"%{test_name}%"))
         
        if city:
            query = query.filter(Provider.city.ilike(f"%{city}%"))
            
        result = query.first()
        
        if not result or result.average is None:
            return json.dumps({"error": f"No pricing data found for {test_name}"})
            
        return json.dumps({
            "test_name": test_name,
            "city": city or "All",
            "lowest_price": float(result.lowest),
            "highest_price": float(result.highest),
            "average_price": round(float(result.average), 2)
        })
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
            
        conditions = [TestPricing.test_name.ilike(f"%{t_name}%") for t_name in test_names]
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
    Calculate the suggested selling price and profit given a base cost and desired margin percentage.
    
    Args:
        cost: The base cost to calculate margin on.
        margin_percentage: The desired profit margin as a percentage (e.g., 20.0 for 20%).
    """
    profit = cost * (margin_percentage / 100.0)
    selling_price = cost + profit
    return json.dumps({
        "base_cost": cost,
        "margin_percentage": margin_percentage,
        "profit": round(profit, 2),
        "suggested_selling_price": round(selling_price, 2)
    })

def build_custom_package(tests: List[str], margin_percentage: float = 0.0) -> str:
    """
    Build a custom health package by aggregating the average market cost of individual tests, 
    then calculating the final package price using the requested margin.
    
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
            
        conditions = [TestPricing.test_name.ilike(f"%{t_name}%") for t_name in tests]
        results = session.query(TestPricing.test_name, func.avg(TestPricing.price).label('avg_price'))\
            .join(Provider, TestPricing.provider_id == Provider.provider_id)\
            .filter(Provider.provider_name == "ES Healthcare")\
            .filter(or_(*conditions))\
            .group_by(TestPricing.test_name).all()
            
        for t_name, avg_price in results:
            avg_val = float(avg_price) if avg_price else 0.0
            total_cost += avg_val
            test_details.append({
                "test": t_name,
                "base_cost": round(avg_val, 2)
            })
            
        profit = total_cost * (margin_percentage / 100.0)
        selling_price = total_cost + profit
        
        return json.dumps({
            "included_tests": test_details,
            "total_base_cost": round(total_cost, 2),
            "margin_percentage": margin_percentage,
            "profit": round(profit, 2),
            "suggested_package_price": round(selling_price, 2)
        })
    finally:
        session.close()

def get_pricing_analysis(status: Optional[str] = None, recommendation: Optional[str] = None, limit: int = 10) -> str:
    """
    Get a list of tests with their market pricing analysis (difference %, status, recommendation).
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
                
            results_list.append({
                "test_name": data["test_name"],
                "city": data["city"],
                "es_price": data["es_price"],
                "market_average": metrics["market_average"],
                "difference_pct": metrics["difference_pct"],
                "status": metrics["status"],
                "recommendation": metrics["recommendation"]
            })
            
        # Sort by absolute difference percentage descending
        results_list.sort(key=lambda x: abs(x["difference_pct"]), reverse=True)
        results_list = results_list[:limit]
        
        if not results_list:
            return json.dumps({"message": "No tests found matching criteria."})
            
        return json.dumps({"analyzed_tests": results_list})
    finally:
        session.close()
