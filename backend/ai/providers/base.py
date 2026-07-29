"""
Base AI provider abstract class.
"""

import abc


class BaseAIProvider(abc.ABC):
    """Abstract base class for all AI providers (Groq, OpenRouter, etc.)."""

    @abc.abstractmethod
    def provider_name(self) -> str:
        pass

    @abc.abstractmethod
    def model_name(self) -> str:
        pass

    @abc.abstractmethod
    async def health_check(self) -> bool:
        pass

    @abc.abstractmethod
    async def generate_response(
        self,
        messages,
        settings,
        execute_tool_cb,
        parse_text_tool_calls_cb,
        sanitize_response_cb,
        tools_schema,
        max_rounds,
        llm_logger,
        start_time,
        faq_cache_cb,
    ):
        pass
