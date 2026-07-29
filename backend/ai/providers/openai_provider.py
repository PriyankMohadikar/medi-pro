"""
OpenAI-compatible AI provider implementations.

Includes the base OpenAICompatibleProvider and concrete subclasses
for Groq and OpenRouter.
"""

import asyncio
import json
import time

import openai
from fastapi.responses import StreamingResponse

from ai.providers.base import BaseAIProvider
from ai.prompts.system_prompt import FINAL_ANSWER_PROMPT, TOOL_RESULT_FOLLOWUP_PROMPT


class ProviderException(Exception):
    """Exception raised when a provider fails to generate a response before streaming."""
    pass


class OpenAICompatibleProvider(BaseAIProvider):
    def __init__(self, provider_name, api_key, base_url, model_name):
        self._provider_name = provider_name
        self._api_key = api_key
        self._base_url = base_url
        self._model_name = model_name
        if self._api_key:
            self.client = openai.AsyncOpenAI(
                api_key=self._api_key, base_url=self._base_url
            )
        else:
            self.client = None

    def provider_name(self) -> str:
        return self._provider_name

    def model_name(self) -> str:
        return self._model_name

    async def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            await asyncio.wait_for(self.client.models.list(), timeout=5.0)
            return True
        except Exception:
            return False

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
        if not self.client:
            raise ProviderException(f"The AI service is not configured. Please set the API key for {self._provider_name}.")

        for round_num in range(max_rounds):
            response = None
            for attempt in range(2):
                try:
                    response = await self.client.chat.completions.create(
                        model=self._model_name,
                        messages=messages,
                        tools=tools_schema,
                        temperature=settings.TEMPERATURE,
                    )
                    break
                except Exception as e:
                    llm_logger.warning(
                        f"{self._provider_name} attempt {attempt + 1} failed: {e}"
                    )
                    if attempt == 0:
                        await asyncio.sleep(1)
                    else:
                        raise ProviderException(f"{self._provider_name} failed: {e}")

            if not response:
                raise ProviderException(f"{self._provider_name} is temporarily unavailable.")

            response_message = response.choices[0].message
            api_tool_calls = response_message.tool_calls or []
            content_text = response_message.content or ""
            text_tool_calls = (
                parse_text_tool_calls_cb(content_text) if content_text else []
            )

            if not api_tool_calls and not text_tool_calls:
                final_text = sanitize_response_cb(content_text)
                if faq_cache_cb:
                    faq_cache_cb(final_text)
                llm_logger.info(
                    f"{self._provider_name} response (round {round_num + 1}, no tools): "
                    f"{round(time.time() - start_time, 2)}s"
                )

                async def stream():
                    yield final_text

                return StreamingResponse(stream(), media_type="text/plain")

            if api_tool_calls:
                messages.append(response_message.model_dump(exclude_none=True))
                for tool_call in api_tool_calls:
                    function_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    llm_logger.info(
                        f"{self._provider_name} API tool call (round {round_num + 1}): "
                        f"{function_name}({arguments})"
                    )
                    tool_response = await execute_tool_cb(function_name, arguments)
                    llm_logger.info(f"TOOL RESULT PAYLOAD: {tool_response}")
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": tool_response,
                        }
                    )
            elif text_tool_calls:
                for fn_name, fn_args in text_tool_calls:
                    llm_logger.info(
                        f"{self._provider_name} text tool call (round {round_num + 1}): "
                        f"{fn_name}({fn_args})"
                    )
                    tool_response = await execute_tool_cb(fn_name, fn_args)
                    llm_logger.info(f"TOOL RESULT PAYLOAD: {tool_response}")
                    messages.append(
                        {
                            "role": "user",
                            "content": TOOL_RESULT_FOLLOWUP_PROMPT.format(
                                tool_response=tool_response
                            ),
                        }
                    )

        messages.append({"role": "user", "content": FINAL_ANSWER_PROMPT})

        try:
            final_response_stream = await self.client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                stream=True,
                temperature=settings.TEMPERATURE,
            )

            async def stream_generator():
                full_response = ""
                try:
                    async for chunk in final_response_stream:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            yield content
                    sanitized = sanitize_response_cb(full_response)
                    if faq_cache_cb:
                        faq_cache_cb(sanitized)

                    resp_time = round(time.time() - start_time, 2)
                    debug_info = {
                        "Intent": "General Chat/Tool execution",
                        "Function Selected": [
                            m.get("name") for m in messages if m.get("role") == "tool"
                        ],
                        "Provider": self._provider_name,
                        "Model": self._model_name,
                        "Response Time": f"{resp_time}s",
                        "Final Response Length": len(sanitized),
                    }
                    llm_logger.info(f"DEBUG_MODE_STATS: {json.dumps(debug_info)}")

                except Exception as e:
                    llm_logger.error(f"{self._provider_name} stream error: {e}")
                    if not full_response:
                        yield "I encountered an issue generating the response. Please try again."

            return StreamingResponse(stream_generator(), media_type="text/plain")

        except Exception as e:
            # If the final completion call fails before streaming starts
            raise ProviderException(f"{self._provider_name} failed during final answer generation: {e}")

class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, settings, key_index=1):
        api_key = settings.GROQ_API_KEY_1 if key_index == 1 else settings.GROQ_API_KEY_2
        super().__init__(
            provider_name=f"groq{key_index}",
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            model_name=settings.GROQ_MODEL,
        )


class OpenRouterProvider(OpenAICompatibleProvider):
    def __init__(self, settings, key_index=1):
        api_key = settings.OPENROUTER_API_KEY_1 if key_index == 1 else settings.OPENROUTER_API_KEY_2
        super().__init__(
            provider_name=f"openrouter{key_index}",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model_name=settings.OPENROUTER_MODEL,
        )
