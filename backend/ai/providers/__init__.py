"""Providers subpackage — AI provider implementations and factory."""

from ai.providers.base import BaseAIProvider
from ai.providers.openai_provider import (
    OpenAICompatibleProvider,
    GroqProvider,
    OpenRouterProvider,
    ProviderException
)

def get_provider(provider_name: str, settings) -> BaseAIProvider:
    """Factory function to create the appropriate AI provider."""
    provider_name = provider_name.lower()
    if provider_name == "groq1":
        return GroqProvider(settings, key_index=1)
    elif provider_name == "groq2":
        return GroqProvider(settings, key_index=2)
    elif provider_name == "openrouter1":
        return OpenRouterProvider(settings, key_index=1)
    elif provider_name == "openrouter2":
        return OpenRouterProvider(settings, key_index=2)
    
    # Default to groq2 if unknown
    return GroqProvider(settings, key_index=2)


__all__ = [
    "BaseAIProvider",
    "OpenAICompatibleProvider",
    "GroqProvider",
    "OpenRouterProvider",
    "ProviderException",
    "get_provider",
]
