"""
AI module for MediPrice Pro.

Isolates all AI-related functionality: prompts, tool definitions,
tool execution with validation, LLM providers, response sanitization,
caching, and conversation context management.

Usage:
    from ai import chat_router
    app.include_router(chat_router)
"""

from ai.router import router as chat_router
from ai.providers import get_provider

__all__ = ["chat_router", "get_provider"]
