"""
Text-based tool call parser.

Some LLM models (especially free-tier via OpenRouter) emit tool calls as raw
text instead of using the API's structured tool_calls field. This module
extracts those calls so they can be executed server-side.
"""

import json
import re

from ai.tools.executor import VALID_TOOL_NAMES


def parse_text_tool_calls(text: str) -> list:
    """
    Extract tool calls from raw text that non-compliant models emit.

    Handles formats like:
      <tool_call> {"name": "fn", "arguments": {...}} </tool_call>
      <function=fn_name> <parameter=key> value </parameter> </function>
      {"name": "fn", "arguments": {...}}

    Returns list of (function_name, arguments_dict) tuples.
    """
    tool_calls = []

    # Pattern 1: <tool_call> ... </tool_call>
    tc_pattern = re.compile(
        r'<tool_call>\s*(.*?)\s*</tool_call>',
        re.DOTALL | re.IGNORECASE
    )
    for match in tc_pattern.finditer(text):
        try:
            data = json.loads(match.group(1))
            name = data.get("name", "")
            args = data.get("arguments", {})
            if isinstance(args, str):
                args = json.loads(args)
            if name in VALID_TOOL_NAMES:
                tool_calls.append((name, args))
        except (json.JSONDecodeError, KeyError):
            pass

    # Pattern 2: <function=fn_name> <parameter=key> value </parameter> ... </function>
    fn_pattern = re.compile(
        r'<function=(\w+)>\s*(.*?)\s*</function>',
        re.DOTALL | re.IGNORECASE
    )
    for match in fn_pattern.finditer(text):
        fn_name = match.group(1)
        params_text = match.group(2)
        if fn_name in VALID_TOOL_NAMES:
            args = {}
            param_pattern = re.compile(
                r'<parameter=(\w+)>\s*(.*?)\s*</parameter>',
                re.DOTALL | re.IGNORECASE
            )
            for pm in param_pattern.finditer(params_text):
                key = pm.group(1)
                val = pm.group(2).strip()
                try:
                    args[key] = json.loads(val)
                except (json.JSONDecodeError, ValueError):
                    args[key] = val
            tool_calls.append((fn_name, args))

    # Pattern 3: Bare JSON with "name" and "arguments" at the top level
    if not tool_calls:
        json_pattern = re.compile(
            r'\{[^{}]*"name"\s*:\s*"(\w+)"[^{}]*"arguments"\s*:\s*(\{[^{}]*\})[^{}]*\}',
            re.DOTALL,
        )
        for match in json_pattern.finditer(text):
            fn_name = match.group(1)
            try:
                args = json.loads(match.group(2))
                if fn_name in VALID_TOOL_NAMES:
                    tool_calls.append((fn_name, args))
            except json.JSONDecodeError:
                pass

    return tool_calls


def contains_tool_call_text(text: str) -> bool:
    """Check if text contains raw tool call patterns that should not be shown to the user."""
    patterns = [
        r'<tool_call>',
        r'</tool_call>',
        r'<function_call>',
        r'</function_call>',
        r'<function=\w+>',
        r'</function>',
        r'"name"\s*:\s*"(get_market_average|compare_tests|compare_packages|calculate_margin|build_custom_package|get_pricing_analysis|get_test_profitability|get_discount_analysis|build_profitable_package)"',
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
