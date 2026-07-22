import abc
import asyncio
import time
import json
import ollama
import openai
from fastapi.responses import StreamingResponse

class BaseAIProvider(abc.ABC):
    
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
    async def generate_response(self, messages, settings, execute_tool_cb, parse_text_tool_calls_cb, sanitize_response_cb, tools_schema, max_rounds, llm_logger, start_time, faq_cache_cb):
        pass


class OllamaProvider(BaseAIProvider):
    def __init__(self, settings):
        self.settings = settings
        self.client = ollama.AsyncClient(host=settings.OLLAMA_HOST)
        
    def provider_name(self) -> str:
        return "ollama"
        
    def model_name(self) -> str:
        return self.settings.OLLAMA_MODEL
        
    async def health_check(self) -> bool:
        try:
            # Short timeout ping to Ollama
            await asyncio.wait_for(self.client.tags(), timeout=3.0)
            return True
        except Exception:
            return False
            
    async def generate_response(self, messages, settings, execute_tool_cb, parse_text_tool_calls_cb, sanitize_response_cb, tools_schema, max_rounds, llm_logger, start_time, faq_cache_cb):
        for round_num in range(max_rounds):
            response = await self.client.chat(
                model=self.settings.OLLAMA_MODEL,
                messages=messages,
                tools=tools_schema,
                options={'temperature': settings.TEMPERATURE, 'num_predict': settings.NUM_PREDICT, 'top_p': settings.TOP_P}
            )
            
            response_msg = response['message']
            messages.append(response_msg)
            
            # Check for API-level tool calls
            tool_calls_found = response_msg.get('tool_calls', [])
            
            # Also check for text-based tool calls in the content
            content_text = response_msg.get('content', '') or ''
            text_tool_calls = parse_text_tool_calls_cb(content_text) if content_text else []
            
            if not tool_calls_found and not text_tool_calls:
                final_text = sanitize_response_cb(content_text)
                if faq_cache_cb: faq_cache_cb(final_text)
                llm_logger.info(f"Ollama response (round {round_num + 1}, no tools): {round(time.time() - start_time, 2)}s")
                async def stream():
                    yield final_text
                return StreamingResponse(stream(), media_type="text/plain")
            
            # Execute API-level tool calls
            if tool_calls_found:
                for tool in tool_calls_found:
                    function_name = tool['function']['name']
                    arguments = tool['function']['arguments']
                    llm_logger.info(f"Ollama tool call (round {round_num + 1}): {function_name}({arguments})")
                    tool_response = await execute_tool_cb(function_name, arguments)
                    messages.append({'role': 'tool', 'content': tool_response, 'name': function_name})
            
            # Execute text-based tool calls
            if text_tool_calls:
                for fn_name, fn_args in text_tool_calls:
                    llm_logger.info(f"Ollama text tool call (round {round_num + 1}): {fn_name}({fn_args})")
                    tool_response = await execute_tool_cb(fn_name, fn_args)
                    messages.append({'role': 'tool', 'content': tool_response, 'name': fn_name})
        
        # Final round: force natural language, no tools
        messages.append({
            "role": "user",
            "content": "Now provide your final answer as a professional consultant using the exact format: 1. 📋 Summary, 2. 📊 Detailed Analysis, 3. 📦 Data / Pricing Details. DO NOT USE MARKDOWN TABLES. Do NOT call any more tools or functions."
        })
        
        final_response_stream = await self.client.chat(
            model=self.settings.OLLAMA_MODEL,
            messages=messages,
            stream=True,
            options={'temperature': settings.TEMPERATURE, 'num_predict': settings.NUM_PREDICT, 'top_p': settings.TOP_P}
        )
        
        async def stream_generator():
            full_response = ""
            try:
                async for chunk in final_response_stream:
                    if 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        full_response += content
                        yield content
                sanitized = sanitize_response_cb(full_response)
                if faq_cache_cb: faq_cache_cb(sanitized)
                
                resp_time = round(time.time() - start_time, 2)
                debug_info = {
                    "Intent": "General Chat/Tool execution",
                    "Function Selected": [m.get('name') for m in messages if m.get('role') == 'tool'],
                    "Provider": self.provider_name(),
                    "Model": self.model_name(),
                    "Response Time": f"{resp_time}s",
                    "Final Response Length": len(sanitized)
                }
                llm_logger.info(f"DEBUG_MODE_STATS: {json.dumps(debug_info)}")
                
            except Exception as e:
                llm_logger.error(f"Ollama stream error: {e}")
                if not full_response:
                    yield "I encountered an issue generating the response. Please try again."
        
        return StreamingResponse(stream_generator(), media_type="text/plain")


class OpenAICompatibleProvider(BaseAIProvider):
    def __init__(self, provider_name, api_key, base_url, model_name):
        self._provider_name = provider_name
        self._api_key = api_key
        self._base_url = base_url
        self._model_name = model_name
        if self._api_key:
            self.client = openai.AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
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
            # We fetch models endpoint as a quick health check
            await asyncio.wait_for(self.client.models.list(), timeout=5.0)
            return True
        except Exception:
            return False
            
    async def generate_response(self, messages, settings, execute_tool_cb, parse_text_tool_calls_cb, sanitize_response_cb, tools_schema, max_rounds, llm_logger, start_time, faq_cache_cb):
        if not self.client:
            async def error_stream():
                yield f"The AI service is not configured. Please set the API key for {self._provider_name}."
            return StreamingResponse(error_stream(), media_type="text/plain")
            
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
                    llm_logger.warning(f"{self._provider_name} attempt {attempt + 1} failed: {e}")
                    if attempt == 0:
                        await asyncio.sleep(1)
                    else:
                        raise
            
            if not response:
                async def error_stream():
                    yield "The AI service is temporarily unavailable. Please try again in a moment."
                return StreamingResponse(error_stream(), media_type="text/plain")
            
            response_message = response.choices[0].message
            api_tool_calls = response_message.tool_calls or []
            content_text = response_message.content or ""
            text_tool_calls = parse_text_tool_calls_cb(content_text) if content_text else []
            
            if not api_tool_calls and not text_tool_calls:
                final_text = sanitize_response_cb(content_text)
                if faq_cache_cb: faq_cache_cb(final_text)
                llm_logger.info(f"{self._provider_name} response (round {round_num + 1}, no tools): {round(time.time() - start_time, 2)}s")
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
                    llm_logger.info(f"{self._provider_name} API tool call (round {round_num + 1}): {function_name}({arguments})")
                    tool_response = await execute_tool_cb(function_name, arguments)
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_response
                    })
            elif text_tool_calls:
                for fn_name, fn_args in text_tool_calls:
                    llm_logger.info(f"{self._provider_name} text tool call (round {round_num + 1}): {fn_name}({fn_args})")
                    tool_response = await execute_tool_cb(fn_name, fn_args)
                    messages.append({
                        "role": "user",
                        "content": f"Here are the results from the database for your analysis:\n{tool_response}\n\nNow provide a professional natural-language response based on this data. Do NOT use any tool calls or function calls. Write your response as a healthcare pricing consultant."
                    })
        
        messages.append({
            "role": "user",
            "content": "Now provide your final answer as a professional consultant using the exact format: 1. 📋 Summary, 2. 📊 Detailed Analysis, 3. 📦 Data / Pricing Details. DO NOT USE MARKDOWN TABLES. Do NOT call any more tools or functions."
        })
        
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
                    if faq_cache_cb: faq_cache_cb(sanitized)
                    
                    resp_time = round(time.time() - start_time, 2)
                    debug_info = {
                        "Intent": "General Chat/Tool execution",
                        "Function Selected": [m.get('name') for m in messages if m.get('role') == 'tool'],
                        "Provider": self._provider_name,
                        "Model": self._model_name,
                        "Response Time": f"{resp_time}s",
                        "Final Response Length": len(sanitized)
                    }
                    llm_logger.info(f"DEBUG_MODE_STATS: {json.dumps(debug_info)}")
                    
                except Exception as e:
                    llm_logger.error(f"{self._provider_name} stream error: {e}")
                    if not full_response:
                        yield "I encountered an issue generating the response. Please try again."
            
            return StreamingResponse(stream_generator(), media_type="text/plain")
            
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            status_code = getattr(e, 'status_code', getattr(e, 'status', 'N/A'))
            response_body = getattr(getattr(e, 'response', None), 'text', getattr(e, 'message', 'N/A'))
            llm_logger.error(f"{self._provider_name} final turn error details:\nType: {type(e).__name__}\nStatus: {status_code}\nBody: {response_body}\nTrace:\n{tb}")
            async def error_stream():
                yield f"The AI service encountered an issue. Please try again in a moment. Error: {type(e).__name__}"
            return StreamingResponse(error_stream(), media_type="text/plain")


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, settings):
        super().__init__(
            provider_name="groq",
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            model_name=settings.GROQ_MODEL
        )


class OpenRouterProvider(OpenAICompatibleProvider):
    def __init__(self, settings):
        super().__init__(
            provider_name="openrouter",
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model_name=settings.OPENROUTER_MODEL
        )

def get_provider(provider_name: str, settings) -> BaseAIProvider:
    provider_name = provider_name.lower()
    if provider_name == "groq":
        return GroqProvider(settings)
    elif provider_name == "openrouter":
        return OpenRouterProvider(settings)
    else:
        return OllamaProvider(settings)
