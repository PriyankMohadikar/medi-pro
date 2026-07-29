"""
Response sanitizer — strips leaked internal artifacts from LLM output.
"""

import re

def sanitize_response(text: str) -> str:
    """Remove any internal implementation details that leaked into the response."""
    from ai.tools.executor import VALID_TOOL_NAMES

    if not text:
        return text

    # Remove <tool_call>...</tool_call> blocks
    text = re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove <function_call>...</function_call> blocks
    text = re.sub(r'<function_call>.*?</function_call>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove <function=...>...</function> blocks
    text = re.sub(r'<function=\w+>.*?</function>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove [Stream Error: ...] markers
    text = re.sub(r'\[Stream Error:.*?\]', '', text, flags=re.DOTALL)

    # Remove bare JSON blocks that look like tool calls ({"name": "...", "arguments": ...})
    text = re.sub(
        r'\{[^{}]*"name"\s*:\s*"[^"]*"[^{}]*"arguments"\s*:\s*\{[^{}]*\}[^{}]*\}',
        '', text, flags=re.DOTALL
    )

    # Remove lines that are just function names or tool references
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip().lower()
        # Skip lines that are just internal function names
        if stripped in VALID_TOOL_NAMES:
            continue
        # Skip lines that reference internal details
        if any(marker in stripped for marker in [
            'traceback', 'file "/', 'error executing tool', 'sqlalchemy', 'psycopg2'
        ]):
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)

    # Clean up excessive whitespace from removals
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    # If the entire response was stripped (nothing left), return a fallback
    if not text or len(text) < 10:
        return (
            "I wasn't able to generate a complete response for that query. "
            "Could you please rephrase your question? For example, try asking "
            "about specific test prices, package comparisons, or pricing recommendations."
        )

    return text
