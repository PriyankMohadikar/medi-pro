"""
Thin FastAPI router for the AI chat endpoint.

This module is responsible only for:
- Defining the HTTP endpoint and request/response models
- Wiring together the AI submodules (prompts, tools, providers, services)
- Logging and error handling

All business logic is delegated to the ai submodules.
"""

import logging
import os
import time
import json

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_session_factory, get_engine
from config import load_settings

from ai.prompts import SYSTEM_PROMPT
from ai.tools import execute_tool, OPENAI_TOOLS, parse_text_tool_calls
from ai.services import sanitize_response, FAQCache
from ai.providers import get_provider
from ai.providers.openai_provider import ProviderException

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("api_server.chat")
llm_logger = logging.getLogger("llm")
llm_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/llm.log")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
)
llm_logger.addHandler(file_handler)

router = APIRouter()

settings = load_settings()
engine = get_engine(settings)
SessionFactory = get_session_factory(engine)


def get_db() -> Session:
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    provider: Optional[str] = None


# Module-level FAQ cache
faq_cache = FAQCache()

MAX_TOOL_ROUNDS = 3  # Prevent infinite tool-call loops

DEFAULT_PRIORITY = ["groq2", "openrouter2", "groq1", "openrouter1"]

def get_provider_list(requested_provider: Optional[str]) -> List[str]:
    requested_provider = (requested_provider or "automatic").lower()
    if requested_provider in DEFAULT_PRIORITY:
        return [requested_provider] + [p for p in DEFAULT_PRIORITY if p != requested_provider]
    return DEFAULT_PRIORITY


@router.get("/api/chat/health")
async def chat_health(provider: str = "automatic"):
    """Health check for AI provider with failover support."""
    provider_list = get_provider_list(provider)
    for provider_name in provider_list:
        ai_provider = get_provider(provider_name, settings)
        is_healthy = await ai_provider.health_check()
        if is_healthy:
            return {"status": "ok", "provider": provider_name}
            
    raise HTTPException(
        status_code=503, detail="All AI providers are unreachable."
    )


@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    llm_logger.info(f"Chat request received: {request.message[:80]}...")

    # Determine priority list of providers
    provider_list = get_provider_list(request.provider)



    try:
        # Audit prompt length
        system_len = len(SYSTEM_PROMPT)
        history_len = (
            sum(len(m.content) for m in request.history) if request.history else 0
        )
        msg_len = len(request.message)
        total_chars = system_len + history_len + msg_len
        est_tokens = total_chars // 4

        llm_logger.info(
            f"Prompt Audit: Sys={system_len} chars, Hist={history_len} chars, "
            f"Msg={msg_len} chars. Est tokens: {est_tokens}"
        )

        # Automatically reduce if excessively large
        if est_tokens > 2000 and request.history:
            llm_logger.warning("Prompt excessively large. Truncating history.")
            request.history = request.history[-2:]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if request.history:
            for msg in request.history[-4:]:
                messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": request.message})

        last_error = None
        for provider_name in provider_list:
            ai_provider = get_provider(provider_name, settings)
            try:
                # We do not pass deep copy of messages since they might be mutated with tool calls
                # However, if it fails early, tool calls wouldn't be appended yet.
                messages_copy = [dict(m) for m in messages]
                
                return await ai_provider.generate_response(
                    messages=messages_copy,
                    settings=settings,
                    execute_tool_cb=execute_tool,
                    parse_text_tool_calls_cb=parse_text_tool_calls,
                    sanitize_response_cb=sanitize_response,
                    tools_schema=OPENAI_TOOLS,
                    max_rounds=MAX_TOOL_ROUNDS,
                    llm_logger=llm_logger,
                    start_time=start_time,
                    faq_cache_cb=None,
                )
            except ProviderException as pe:
                llm_logger.warning(f"Failover triggered: {provider_name} failed. Reason: {pe}")
                last_error = pe
                continue

        # If loop exits without returning, all providers failed
        llm_logger.error(f"All AI providers failed. Last error: {last_error}")
        async def error_stream():
            yield "I couldn't generate a response because all AI providers are currently unavailable. Please try again in a few moments."
        return StreamingResponse(error_stream(), media_type="text/plain")

    except HTTPException:
        raise
    except Exception as e:
        import traceback

        tb = traceback.format_exc()
        status_code = getattr(e, "status_code", getattr(e, "status", "N/A"))
        response_body = getattr(
            getattr(e, "response", None), "text", getattr(e, "message", "N/A")
        )

        error_msg = (
            f"Exception Type: {type(e).__name__}\n"
            f"HTTP Status: {status_code}\n"
            f"Provider Response: {response_body}\n"
            f"Stack Trace:\n{tb}"
        )
        llm_logger.error(f"Chat API Error Detailed Logging:\n{error_msg}")

        async def general_error_stream():
            yield "I couldn't generate a response because all AI providers are currently unavailable. Please try again in a few moments."

        return StreamingResponse(general_error_stream(), media_type="text/plain")
