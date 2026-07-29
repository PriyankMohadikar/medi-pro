"""
Data validation layer for AI tool results.

Validates every tool result before the LLM sees it, annotating with
confidence metadata so the AI knows exactly which data is verified
versus missing — preventing hallucinated financial values.
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ai.validator")

# Fields that indicate financial data availability per tool
_TOOL_EXPECTED_FIELDS: Dict[str, Dict[str, List[str]]] = {
    "get_market_average": {
        "critical": ["average_price"],
        "profitability": ["es_price", "internal_cost", "es_profit", "es_margin_pct"],
        "market": ["lowest_price", "highest_price"],
    },
    "compare_tests": {
        "critical": ["test_comparisons"],
    },
    "compare_packages": {
        "critical": ["package_comparisons"],
    },
    "calculate_margin": {
        "critical": ["required_selling_price", "expected_profit"],
    },
    "build_custom_package": {
        "critical": ["total_base_cost", "suggested_package_price", "included_tests"],
        "profitability": ["total_internal_cost", "package_profit", "package_margin_pct"],
    },
    "get_pricing_analysis": {
        "critical": ["analyzed_tests"],
    },
    "get_test_profitability": {
        "critical": ["profitability_data"],
    },
    "get_discount_analysis": {
        "critical": ["discount_analysis"],
    },
    "build_profitable_package": {
        "critical": [
            "total_individual_es_price",
            "suggested_package_price",
            "total_internal_cost",
        ],
        "profitability": [
            "actual_margin_pct",
            "expected_profit",
            "customer_savings",
            "customer_savings_pct",
            "is_financially_viable",
        ],
    },
}


def validate_tool_result(tool_name: str, raw_result: str) -> str:
    """
    Validate a tool result and annotate it with confidence metadata.

    Args:
        tool_name: Name of the tool that produced the result.
        raw_result: JSON string returned by the tool function.

    Returns:
        JSON string with '_validation' metadata injected.
    """
    try:
        data = json.loads(raw_result)
    except (json.JSONDecodeError, TypeError):
        # If the result isn't valid JSON, return as-is with a warning
        return json.dumps({
            "error": "Invalid tool result format",
            "_validation": {
                "confidence": "Low",
                "verified_fields": [],
                "missing_fields": [],
                "data_warning": "The tool returned an invalid response. No financial data is available for this query.",
            },
        })

    # If the result is an error, annotate and return
    if "error" in data:
        data["_validation"] = {
            "confidence": "Low",
            "verified_fields": [],
            "missing_fields": [],
            "data_warning": f"Data retrieval failed: {data['error']}. Do not estimate or fabricate any values.",
        }
        return json.dumps(data)

    # If the result is a simple message (e.g., "No tests found"), annotate
    if "message" in data and len(data) == 1:
        data["_validation"] = {
            "confidence": "Low",
            "verified_fields": [],
            "missing_fields": [],
            "data_warning": data["message"],
        }
        return json.dumps(data)

    # Get expected fields for this tool
    expected = _TOOL_EXPECTED_FIELDS.get(tool_name, {})
    if not expected:
        # Unknown tool — pass through with basic annotation
        data["_validation"] = {
            "confidence": "Medium",
            "verified_fields": list(data.keys()),
            "missing_fields": [],
            "data_warning": None,
        }
        return json.dumps(data)

    # Check field availability
    verified = []
    missing = []

    for category_fields in expected.values():
        for field in category_fields:
            if field in data and data[field] is not None:
                verified.append(field)
            else:
                missing.append(field)

    # Also check nested test details for package tools
    _check_nested_test_details(tool_name, data, verified, missing)

    # Calculate confidence
    critical_fields = expected.get("critical", [])
    critical_present = all(
        f in data and data[f] is not None for f in critical_fields
    )
    profitability_fields = expected.get("profitability", [])
    profitability_present = all(
        f in data and data[f] is not None for f in profitability_fields
    ) if profitability_fields else True

    if critical_present and profitability_present and not missing:
        confidence = "High"
    elif critical_present and len(missing) <= 2:
        confidence = "Medium"
    else:
        confidence = "Low"

    # Build warning message
    data_warning = None
    if missing:
        missing_readable = [f.replace("_", " ").title() for f in missing]
        data_warning = (
            f"The following data is unavailable: {', '.join(missing_readable)}. "
            "Analysis is limited to verified fields only. "
            "Do not estimate or fabricate values for missing data."
        )

    data["_validation"] = {
        "confidence": confidence,
        "verified_fields": verified,
        "missing_fields": missing,
        "data_warning": data_warning,
    }

    return json.dumps(data)


def _check_nested_test_details(
    tool_name: str,
    data: dict,
    verified: list,
    missing: list,
) -> None:
    """Check nested test detail objects in package results for missing cost data."""
    tests_key = None
    if tool_name in ("build_custom_package", "build_profitable_package"):
        tests_key = "included_tests"
    
    if not tests_key or tests_key not in data:
        return

    tests = data.get(tests_key, [])
    if not isinstance(tests, list):
        return

    tests_missing_cost = []
    for test_detail in tests:
        if not isinstance(test_detail, dict):
            continue
        test_name = test_detail.get("test", test_detail.get("test_name", "Unknown"))
        if "internal_cost" not in test_detail:
            tests_missing_cost.append(test_name)

    if tests_missing_cost:
        missing.append("per_test_internal_costs")
        if "missing_cost_tests" not in data:
            data["_missing_cost_tests"] = tests_missing_cost
