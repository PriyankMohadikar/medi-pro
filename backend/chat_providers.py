"""
Compatibility shim — redirects imports to the new ai/ module.

This file previously contained all AI provider logic (~307 lines).
It has been refactored into the backend/ai/providers/ package.

For direct usage, import from ai/ instead:
    from ai.providers import get_provider
    from ai.providers.base import BaseAIProvider
"""

# Re-export for backward compatibility
from ai.providers import get_provider
from ai.providers.base import BaseAIProvider
from ai.providers.ollama_provider import OllamaProvider
from ai.providers.openai_provider import (
    OpenAICompatibleProvider,
    GroqProvider,
    OpenRouterProvider,
)
