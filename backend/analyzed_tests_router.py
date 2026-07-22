from typing import Optional, List, Dict, Any
import math
import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_session_factory, get_engine
from config import load_settings
from models import TestPricing, Provider
from analysis_logic import calculate_pricing_metrics

router = APIRouter()
settings = load_settings()
engine = get_engine(settings)
SessionFactory = get_session_factory(engine)

def get_db() -> Session:
    return SessionFactory()

class AnalyzedTestResponse(BaseModel):
    test_name: str
    category: str
    city: str
    es_price: float
    lowest_price: float
    highest_price: float
    market_average: float
    difference_pct: float
    status: str
    recommendation: str

class PaginatedAnalyzedTests(BaseModel):
    items: List[AnalyzedTestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    # Summary stats for the frontend KPI cards
    total_tests: int
    competitive_tests: int
    needs_review_tests: int
    overpriced_tests: int
    underpriced_tests: int
    average_difference_pct: float

    # Quick insights
    top_5_overpriced: List[Dict[str, Any]]
    top_5_competitive: List[Dict[str, Any]]
    top_5_lowest: List[Dict[str, Any]]
    most_expensive_category: str
    most_competitive_category: str

@router.get("/api/analyzed-tests", response_model=PaginatedAnalyzedTests)
def get_analyzed_tests(
    city: Optional[str] = Query("All", description="Filter by city"),
    category: Optional[str] = Query("All", description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by test name"),
    status: Optional[str] = Query("All", description="Filter by status"),
    recommendation: Optional[str] = Query("All", description="Filter by recommendation"),
    sort_by: Optional[str] = Query("difference_pct", description="Field to sort by"),
    sort_dir: Optional[str] = Query("desc", description="Sort direction (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(15, ge=1, le=100, description="Items per page"),
):
    session = get_db()
    try:
        # First, fetch all tests for "ES Healthcare" 
        # and all tests for other providers to calculate metrics.
        # This can be optimized in SQL, but for ~1000s of tests, python grouping is fine.
        
        # Base query for all tests
        all_tests_query = session.query(TestPricing, Provider).join(Provider, TestPricing.provider_id == Provider.provider_id)
        all_results = all_tests_query.all()
        
        # 1. Extract ES Healthcare baseline prices across all cities
        es_baseline_prices = {}
        for tp, prov in all_results:
            if prov.provider_name == "ES Healthcare" and tp.price:
                test_name_norm = str(tp.test_name).strip().lower()
                es_baseline_prices[test_name_norm] = float(tp.price)
                
        # Group by test_name and city
        grouped_tests: Dict[str, Dict[str, Any]] = {}
        
        for tp, prov in all_results:
            key = f"{tp.test_name}_{prov.city}"
            if key not in grouped_tests:
                grouped_tests[key] = {
                    "test_name": tp.test_name,
                    "category": tp.category,
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
                test_name_norm = str(data["test_name"]).strip().lower()
                data["es_price"] = es_baseline_prices.get(test_name_norm)

        # Process and calculate metrics
        analyzed_list = []
        for key, data in grouped_tests.items():
            if data["es_price"] is None or not data["competitor_prices"]:
                continue # Skip if we don't have ES price or competitors
                
            metrics = calculate_pricing_metrics(data["es_price"], data["competitor_prices"])
            
            analyzed_list.append({
                "test_name": data["test_name"],
                "category": data["category"],
                "city": data["city"],
                "es_price": data["es_price"],
                "lowest_price": metrics["lowest_price"],
                "highest_price": metrics["highest_price"],
                "market_average": metrics["market_average"],
                "difference_pct": metrics["difference_pct"],
                "status": metrics["status"],
                "recommendation": metrics["recommendation"]
            })
            
        # 1. Calculate overall summary stats (BEFORE FILTERING by UI filters, 
        # but AFTER grouping. Wait, user usually wants KPI cards based on the filtered set or global set? 
        # Usually KPIs are based on the filtered dataset so they update when you select a city).
        
        # Apply Filters
        filtered_list = []
        for item in analyzed_list:
            if city and city != "All" and item["city"] != city:
                continue
            if category and category != "All" and item["category"] != category:
                continue
            if status and status != "All" and item["status"] != status:
                continue
            if recommendation and recommendation != "All" and item["recommendation"] != recommendation:
                continue
            if search:
                search_term = search.strip().lower()
                test_name_val = str(item["test_name"]).strip().lower()
                if search_term not in test_name_val:
                    continue
            filtered_list.append(item)
            
        # Calculate KPIs based on filtered list
        total_tests = len(filtered_list)
        competitive_tests = sum(1 for x in filtered_list if x["status"] == "Competitive")
        needs_review_tests = sum(1 for x in filtered_list if x["status"] == "Needs Review")
        overpriced_tests = sum(1 for x in filtered_list if x["status"] == "Overpriced")
        underpriced_tests = sum(1 for x in filtered_list if x["status"] == "Underpriced")
        avg_diff = sum(x["difference_pct"] for x in filtered_list) / total_tests if total_tests > 0 else 0.0

        # Quick Insights
        # Top 5 Overpriced
        top_5_overpriced = sorted([x for x in filtered_list if x["difference_pct"] > 0], 
                                  key=lambda x: x["difference_pct"], reverse=True)[:5]
        # Top 5 Competitive (closest to 0 diff)
        top_5_competitive = sorted(filtered_list, key=lambda x: abs(x["difference_pct"]))[:5]
        # Top 5 Lowest (lowest difference pct)
        top_5_lowest = sorted(filtered_list, key=lambda x: x["difference_pct"])[:5]
        
        # Category stats
        cat_stats = {}
        for x in filtered_list:
            c = x["category"]
            if c not in cat_stats:
                cat_stats[c] = {"total_price": 0, "count": 0, "total_diff": 0}
            cat_stats[c]["total_price"] += x["es_price"]
            cat_stats[c]["count"] += 1
            cat_stats[c]["total_diff"] += abs(x["difference_pct"])
            
        most_expensive_category = "N/A"
        most_competitive_category = "N/A"
        if cat_stats:
            most_expensive_category = max(cat_stats.keys(), key=lambda k: cat_stats[k]["total_price"] / cat_stats[k]["count"])
            most_competitive_category = min(cat_stats.keys(), key=lambda k: cat_stats[k]["total_diff"] / cat_stats[k]["count"])

        # Sorting
        reverse = sort_dir == "desc"
        filtered_list.sort(key=lambda x: x.get(sort_by, 0) if isinstance(x.get(sort_by, 0), (int, float)) else str(x.get(sort_by, "")), reverse=reverse)
        
        # Pagination
        total_items = len(filtered_list)
        total_pages = max(1, math.ceil(total_items / page_size)) if page_size > 0 else 1
        
        # Clamp page to valid range
        page = max(1, min(page, total_pages))
            
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = filtered_list[start_idx:end_idx]

        logging.info(
            f"[analyzed-tests] city={city} category={category} status={status} search={search} "
            f"| total_filtered={total_items} page={page}/{total_pages} items_returned={len(paginated_items)}"
        )

        return PaginatedAnalyzedTests(
            items=paginated_items,
            total=total_items,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_tests=total_tests,
            competitive_tests=competitive_tests,
            needs_review_tests=needs_review_tests,
            overpriced_tests=overpriced_tests,
            underpriced_tests=underpriced_tests,
            average_difference_pct=round(avg_diff, 1),
            top_5_overpriced=[{"name": x["test_name"], "value": x["difference_pct"]} for x in top_5_overpriced],
            top_5_competitive=[{"name": x["test_name"], "value": x["difference_pct"]} for x in top_5_competitive],
            top_5_lowest=[{"name": x["test_name"], "value": x["difference_pct"]} for x in top_5_lowest],
            most_expensive_category=most_expensive_category,
            most_competitive_category=most_competitive_category
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@router.get("/api/export-analyzed-tests")
def export_analyzed_tests(
    city: Optional[str] = Query("All", description="Filter by city"),
    category: Optional[str] = Query("All", description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by test name"),
    status: Optional[str] = Query("All", description="Filter by status"),
    recommendation: Optional[str] = Query("All", description="Filter by recommendation"),
):
    session = get_db()
    try:
        all_tests_query = session.query(TestPricing, Provider).join(Provider, TestPricing.provider_id == Provider.provider_id)
        all_results = all_tests_query.all()
        
        es_baseline_prices = {}
        for tp, prov in all_results:
            if prov.provider_name == "ES Healthcare" and tp.price:
                test_name_norm = str(tp.test_name).strip().lower()
                es_baseline_prices[test_name_norm] = float(tp.price)
                
        grouped_tests: Dict[str, Dict[str, Any]] = {}
        for tp, prov in all_results:
            key = f"{tp.test_name}_{prov.city}"
            if key not in grouped_tests:
                grouped_tests[key] = {
                    "test_name": tp.test_name,
                    "category": tp.category,
                    "city": prov.city,
                    "es_price": None,
                    "competitor_prices": []
                }
            if prov.provider_name == "ES Healthcare":
                grouped_tests[key]["es_price"] = float(tp.price) if tp.price else 0.0
            else:
                if tp.price:
                    grouped_tests[key]["competitor_prices"].append(float(tp.price))

        for key, data in grouped_tests.items():
            if data["es_price"] is None:
                test_name_norm = str(data["test_name"]).strip().lower()
                data["es_price"] = es_baseline_prices.get(test_name_norm)

        analyzed_list = []
        for key, data in grouped_tests.items():
            if data["es_price"] is None or not data["competitor_prices"]:
                continue
                
            metrics = calculate_pricing_metrics(data["es_price"], data["competitor_prices"])
            analyzed_list.append({
                "test_name": data["test_name"],
                "category": data["category"],
                "city": data["city"],
                "es_price": data["es_price"],
                "lowest_price": metrics["lowest_price"],
                "highest_price": metrics["highest_price"],
                "market_average": metrics["market_average"],
                "difference_pct": metrics["difference_pct"],
                "status": metrics["status"],
                "recommendation": metrics["recommendation"]
            })
            
        filtered_list = []
        for item in analyzed_list:
            if city and city != "All" and item["city"] != city:
                continue
            if category and category != "All" and item["category"] != category:
                continue
            if status and status != "All" and item["status"] != status:
                continue
            if recommendation and recommendation != "All" and item["recommendation"] != recommendation:
                continue
            if search:
                search_term = search.strip().lower()
                test_name_val = str(item["test_name"]).strip().lower()
                if search_term not in test_name_val:
                    continue
            filtered_list.append(item)
            
        # Return all filtered items
        return {"items": filtered_list}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
