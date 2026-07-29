"""
Tool execution dispatcher.

Routes tool calls from the LLM to the appropriate chat_services function
and validates the results before returning them.
"""

import json
import logging
import time

import chat_services
from ai.services.validator import validate_tool_result

logger = logging.getLogger("ai.tools.executor")

VALID_TOOL_NAMES = {
    "get_market_average",
    "compare_tests",
    "compare_packages",
    "calculate_margin",
    "build_custom_package",
    "get_pricing_analysis",
    "get_test_profitability",
    "get_discount_analysis",
    "build_profitable_package",
}

# Dispatch table mapping tool names to functions
_TOOL_DISPATCH = {
    "get_market_average": chat_services.get_market_average,
    "compare_tests": chat_services.compare_tests,
    "compare_packages": chat_services.compare_packages,
    "calculate_margin": chat_services.calculate_margin,
    "build_custom_package": chat_services.build_custom_package,
    "get_pricing_analysis": chat_services.get_pricing_analysis,
    "get_test_profitability": chat_services.get_test_profitability,
    "get_discount_analysis": chat_services.get_discount_analysis,
    "build_profitable_package": chat_services.build_profitable_package,
}


async def execute_tool(function_name: str, arguments: dict) -> str:
    """
    Execute a tool function, validate the result, and return as a JSON string.

    The result is passed through the data validator which annotates it with
    confidence metadata before the LLM sees it.
    """
    db_start = time.time()
    try:
        if function_name not in VALID_TOOL_NAMES:
            return json.dumps({"error": f"Unknown tool: {function_name}"})

        tool_fn = _TOOL_DISPATCH[function_name]
        raw_result = tool_fn(**arguments)

        db_time = time.time() - db_start
        if db_time > 10.0:
            logger.warning(
                f"Database operation {function_name} took {round(db_time, 2)}s"
            )

        # Validate and annotate before returning to the LLM
        validated_result = validate_tool_result(function_name, raw_result)

        logger.info(
            f"Tool executed [{function_name}]: "
            f"returned {len(validated_result)} chars in {round(db_time, 2)}s"
        )
        return validated_result

    except Exception as e:
        logger.error(f"Error executing tool {function_name}: {e}", exc_info=True)
        return json.dumps({
            "error": f"Could not retrieve data for this query. Error: {str(e)}",
            "_validation": {
                "confidence": "Low",
                "verified_fields": [],
                "missing_fields": [],
                "data_warning": f"Tool execution failed: {str(e)}. Do not estimate values.",
            },
        })
