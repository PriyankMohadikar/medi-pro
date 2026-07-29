"""
Compatibility shim — redirects imports to the new ai/ module.

This file previously contained all AI chat logic (~727 lines).
It has been refactored into the backend/ai/ package.

For direct usage, import from ai/ instead:
    from ai import chat_router
    from ai.tools import execute_tool
    from ai.prompts import SYSTEM_PROMPT
"""

# Re-export the router for backward compatibility
from ai.router import router

# Re-export key symbols that external scripts might reference
from ai.tools.executor import VALID_TOOL_NAMES, execute_tool
from ai.tools.parser import parse_text_tool_calls, contains_tool_call_text
from ai.services.sanitizer import sanitize_response
from ai.prompts.system_prompt import SYSTEM_PROMPT
