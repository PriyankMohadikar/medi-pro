"""
Tool schema definitions for LLM providers.
"""

# ─── OpenAI-Compatible Tool Schemas ──────────────────────────
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_market_average",
            "description": "Get the lowest, highest, and average market price for a specific test.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string", "description": "Name of the test (e.g., 'CBC', 'Vitamin D')"},
                    "city": {"type": "string", "description": "Optional city to filter by."}
                },
                "required": ["test_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_tests",
            "description": "Compare prices for a list of clinical tests across different providers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of test names to compare (e.g. ['CBC', 'HbA1c'])."
                    },
                    "city": {"type": "string", "description": "Optional city to filter by."}
                },
                "required": ["test_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_packages",
            "description": "Compare prices for health packages across different providers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of package names to compare."
                    },
                    "city": {"type": "string", "description": "Optional city to filter by."}
                },
                "required": ["package_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_margin",
            "description": "Calculate the suggested selling price and profit given a base cost and desired margin percentage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cost": {"type": "number", "description": "The base cost to calculate margin on."},
                    "margin_percentage": {"type": "number", "description": "The desired profit margin as a percentage (e.g., 20.0 for 20%)."}
                },
                "required": ["cost", "margin_percentage"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "build_custom_package",
            "description": "Build a custom health package by aggregating the average market cost of individual tests, then calculating the final package price using the requested margin.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tests": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of test names to include in the package."
                    },
                    "margin_percentage": {"type": "number", "description": "The desired profit margin percentage."}
                },
                "required": ["tests"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pricing_analysis",
            "description": "Get a list of tests with their market pricing analysis (difference %, status, recommendation). Also includes internal cost and profit margin.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Optional status filter (e.g., 'Overpriced', 'Underpriced')."},
                    "recommendation": {"type": "string", "description": "Optional recommendation filter."},
                    "limit": {"type": "integer", "description": "Max number of tests to return (default 10)."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_test_profitability",
            "description": "Get profitability data for ES Healthcare tests: internal cost, profit, margin %, markup %, break-even price, max safe discount, and margin status. Use to answer questions about profit, margin, which tests are most/least profitable, and which can be discounted.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string", "description": "Optional specific test name (e.g., 'CBC'). Omit to get all tests."},
                    "status": {"type": "string", "description": "Optional filter: 'high_margin', 'moderate', 'low_margin', 'loss_making'."},
                    "limit": {"type": "integer", "description": "Max tests to return (default 10)."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_discount_analysis",
            "description": "Analyze whether a discount is safe for a test while maintaining profitability. Identifies tests that can safely be discounted and those that should never be discounted. Can simulate a specific discount percentage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string", "description": "Optional test name. Omit to analyze all tests."},
                    "discount_pct": {"type": "number", "description": "Optional specific discount % to simulate (e.g. 20.0 for 20% off)."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "build_profitable_package",
            "description": "Build a health package with profitability analysis. Calculates total internal cost, suggested price for target margin, expected profit, and customer savings. Use for creating packages with margin targets or price caps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tests": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of test names to include in the package."
                    },
                    "target_margin_pct": {"type": "number", "description": "Desired profit margin percentage (default 30%)."},
                    "max_price": {"type": "number", "description": "Optional maximum package price (e.g. 3000 for 'under 3000')."}
                },
                "required": ["tests"]
            }
        }
    }
]
