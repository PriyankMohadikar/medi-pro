import logging
import asyncio
import time
import json
import re
# Trigger reload again
# Trigger reload again!
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import ollama
from sqlalchemy.orm import Session
import openai

from database import get_session_factory, get_engine
from config import load_settings
from ollama_utils import check_ollama_status
import chat_services
import chat_providers
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("api_server.chat")
llm_logger = logging.getLogger("llm")
llm_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/llm.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
llm_logger.addHandler(file_handler)

router = APIRouter()

settings = load_settings()
engine = get_engine(settings)
SessionFactory = get_session_factory(engine)

# Step 1: Environment Validation & Logging
llm_logger.info(f"AI_PROVIDER={settings.AI_PROVIDER}")
llm_logger.info(f"OPENROUTER_MODEL={settings.OPENROUTER_MODEL}")
if settings.OPENROUTER_API_KEY:
    llm_logger.info(f"OPENROUTER_API_KEY is loaded (length: {len(settings.OPENROUTER_API_KEY)})")
else:
    llm_logger.warning("OPENROUTER_API_KEY is missing!")

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

# ─── System Prompt ────────────────────────────────────────────
# Concise, focused prompt. The LLM is the LAST step — it only
# explains data that FastAPI already fetched from PostgreSQL.
# ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the AI Pricing Consultant for ES Healthcare.
Your purpose is to help management make pricing and package decisions using the PostgreSQL database.

YOUR ROLE:
- Always answer naturally like an experienced healthcare pricing consultant.
- Do not behave like a chatbot. Do not behave like ChatGPT.
- Keep responses professional, concise, and business-focused.

RESPONSE FORMAT (STRICTLY REQUIRED):
Every response MUST be divided into these EXACT sections. Do not use markdown tables.

1. 📋 Summary
Provide 3-5 concise bullet points highlighting the key outcome, business impact, and recommended action.

2. 📊 Detailed Analysis
Explain the reasoning behind the answer in clear business language using available pricing and market data. Mention only the most relevant numbers.

3. 📦 Data / Pricing Details
Present prices, calculations, included tests, and margins as key-value lists or bullet points. Explicitly DO NOT USE markdown tables.

AVAILABLE TOOLS:
- get_market_average: Get lowest, highest, and average market price for a test.
- compare_tests: Compare prices for tests across providers.
- compare_packages: Compare package prices across providers.
- calculate_margin: Calculate selling price and profit from base cost and margin %.
- build_custom_package: Build a custom package from individual tests with margin.
- get_pricing_analysis: Get overpriced/underpriced/competitive analysis for tests.

TEST CATALOG (use exact names when calling tools):
CBC, ESR, FBS, HbA1c, Lipid Profile, LFT, RFT, TSH, Vitamin B12, Vitamin D, Urine Routine, Testosterone, Prolactin, LH (Luteinizing Hormone), Iron Profile, ECG, Doctor Consultation, Breakfast

CRITICAL RULES:
- ABSOLUTELY NO MARKDOWN TABLES. Use bullet points instead.
- Never expose SQL queries, JSON, tool calls, backend logic, or internal implementation.
- If database information is available, always use it. If information is unavailable, clearly state that instead of guessing.

FOR PRICING STRATEGY:
- Recommend prices.
- Explain the reasoning.
- Identify risks.
- Suggest opportunities.

Always sound like a senior healthcare pricing consultant speaking to hospital management.
"""

# ─── Tool Definitions ────────────────────────────────────────

AVAILABLE_TOOLS_OLLAMA = [
    chat_services.get_market_average,
    chat_services.compare_tests,
    chat_services.compare_packages,
    chat_services.calculate_margin,
    chat_services.build_custom_package,
    chat_services.get_pricing_analysis
]

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_market_average",
            "description": "Get the lowest, highest, and average market price for a specific test.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string", "description": "Name of the test (e.g., 'CBC', 'Vitamin D')"},
                    "city": {"type": "string", "description": "Optional city to filter by."}
                },
                "required": ["test_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_tests",
            "description": "Compare prices for a list of clinical tests across different providers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of test names to compare (e.g. ['CBC', 'HbA1c'])."
                    },
                    "city": {"type": "string", "description": "Optional city to filter by."}
                },
                "required": ["test_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_packages",
            "description": "Compare prices for health packages across different providers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of package names to compare."
                    },
                    "city": {"type": "string", "description": "Optional city to filter by."}
                },
                "required": ["package_names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_margin",
            "description": "Calculate the suggested selling price and profit given a base cost and desired margin percentage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cost": {"type": "number", "description": "The base cost to calculate margin on."},
                    "margin_percentage": {"type": "number", "description": "The desired profit margin as a percentage (e.g., 20.0 for 20%)."}
                },
                "required": ["cost", "margin_percentage"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "build_custom_package",
            "description": "Build a custom health package by aggregating the average market cost of individual tests, then calculating the final package price using the requested margin.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tests": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of test names to include in the package."
                    },
                    "margin_percentage": {"type": "number", "description": "The desired profit margin percentage."}
                },
                "required": ["tests"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pricing_analysis",
            "description": "Get a list of tests with their market pricing analysis (difference %, status, recommendation).",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Optional status filter (e.g., 'Overpriced', 'Underpriced')."},
                    "recommendation": {"type": "string", "description": "Optional recommendation filter."},
                    "limit": {"type": "integer", "description": "Max number of tests to return (default 10)."}
                }
            }
        }
    }
]

# ─── FAQ Cache ────────────────────────────────────────────────

class FAQCache:
    def __init__(self):
        self.cache = {}
        self.ttl = 300

    def get(self, key: str):
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['time'] < self.ttl:
                return entry['response']
        return None

    def set(self, key: str, response: str):
        self.cache[key] = {'response': response, 'time': time.time()}

faq_cache = FAQCache()

# ─── Tool Execution ──────────────────────────────────────────

VALID_TOOL_NAMES = {
    "get_market_average", "compare_tests", "compare_packages",
    "calculate_margin", "build_custom_package", "get_pricing_analysis"
}

async def execute_tool(function_name: str, arguments: dict) -> str:
    """Execute a tool function and return the result as a string."""
    db_start = time.time()
    try:
        if function_name not in VALID_TOOL_NAMES:
            return json.dumps({"error": f"Unknown tool: {function_name}"})
            
        if function_name == 'get_market_average':
            tool_response = chat_services.get_market_average(**arguments)
        elif function_name == 'compare_tests':
            tool_response = chat_services.compare_tests(**arguments)
        elif function_name == 'compare_packages':
            tool_response = chat_services.compare_packages(**arguments)
        elif function_name == 'calculate_margin':
            tool_response = chat_services.calculate_margin(**arguments)
        elif function_name == 'build_custom_package':
            tool_response = chat_services.build_custom_package(**arguments)
        elif function_name == 'get_pricing_analysis':
            tool_response = chat_services.get_pricing_analysis(**arguments)
        else:
            tool_response = json.dumps({"error": f"Unknown tool {function_name}"})
            
        db_time = time.time() - db_start
        if db_time > 10.0:
            logger.warning(f"Database operation {function_name} took {round(db_time, 2)}s")
        llm_logger.info(f"Tool executed [Intent: {function_name}]: returned {len(tool_response)} chars in {round(db_time, 2)}s")
        return tool_response
    except Exception as e:
        logger.error(f"Error executing tool {function_name}: {e}", exc_info=True)
        llm_logger.error(f"Error executing tool {function_name}: {e}", exc_info=True)
        return json.dumps({"error": f"Could not retrieve data for this query. Error: {str(e)}"})

# ─── Text-Based Tool Call Parser ──────────────────────────────
# Some models (especially via openrouter/free) emit tool calls as
# raw text instead of using the API's tool_calls field. We parse
# these out so we can execute them server-side.
# ──────────────────────────────────────────────────────────────

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
                # Try to parse as JSON value, fallback to string
                try:
                    args[key] = json.loads(val)
                except (json.JSONDecodeError, ValueError):
                    args[key] = val
            tool_calls.append((fn_name, args))
    
    # Pattern 3: Bare JSON with "name" and "arguments" at the top level
    if not tool_calls:
        json_pattern = re.compile(r'\{[^{}]*"name"\s*:\s*"(\w+)"[^{}]*"arguments"\s*:\s*(\{[^{}]*\})[^{}]*\}', re.DOTALL)
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
        r'"name"\s*:\s*"(get_market_average|compare_tests|compare_packages|calculate_margin|build_custom_package|get_pricing_analysis)"',
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# ─── Response Sanitizer ──────────────────────────────────────
# Strips any residual internal artifacts from the final response.
# ──────────────────────────────────────────────────────────────

def sanitize_response(text: str) -> str:
    """Remove any internal implementation details that leaked into the response."""
    if not text:
        return text
    
    original = text
    
    # Remove <tool_call>...</tool_call> blocks
    text = re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove <function_call>...</function_call> blocks
    text = re.sub(r'<function_call>.*?</function_call>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove <function=...>...</function> blocks
    text = re.sub(r'<function=\w+>.*?</function>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove [Stream Error: ...] markers
    text = re.sub(r'\[Stream Error:.*?\]', '', text, flags=re.DOTALL)
    
    # Remove bare JSON blocks that look like tool calls ({"name": "...", "arguments": ...})
    text = re.sub(r'\{[^{}]*"name"\s*:\s*"[^"]*"[^{}]*"arguments"\s*:\s*\{[^{}]*\}[^{}]*\}', '', text, flags=re.DOTALL)
    
    # Remove lines that are just function names or tool references
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip().lower()
        # Skip lines that are just internal function names
        if stripped in VALID_TOOL_NAMES:
            continue
        # Skip lines that reference internal details
        if any(marker in stripped for marker in ['traceback', 'file "/', 'error executing tool', 'sqlalchemy', 'psycopg2']):
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    
    # Clean up excessive whitespace from removals
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    # If the entire response was stripped (nothing left), return a fallback
    if not text or len(text) < 10:
        return "I wasn't able to generate a complete response for that query. Could you please rephrase your question? For example, try asking about specific test prices, package comparisons, or pricing recommendations."
    
    return text

# ─── Main Chat Endpoint ──────────────────────────────────────

MAX_TOOL_ROUNDS = 3  # Prevent infinite tool-call loops

@router.get("/api/chat/health")
async def chat_health(provider: str = "ollama"):
    """Health check for specific AI provider."""
    ai_provider = chat_providers.get_provider(provider, settings)
    is_healthy = await ai_provider.health_check()
    if is_healthy:
        return {"status": "ok", "provider": ai_provider.provider_name()}
    else:
        raise HTTPException(status_code=503, detail=f"Provider {provider} is unreachable.")

@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    llm_logger.info(f"Chat request received: {request.message[:80]}...")
    
    # Determine provider (from request payload or fallback to settings)
    provider_name = (request.provider or settings.AI_PROVIDER).lower()
    ai_provider = chat_providers.get_provider(provider_name, settings)

    # Check cache
    cached_response = faq_cache.get(request.message.strip().lower())
    if cached_response:
        llm_logger.info("Serving from cache.")
        async def cache_stream():
            yield cached_response
        return StreamingResponse(cache_stream(), media_type="text/plain")

    try:
        # Step 4: Build messages and audit prompt length
        system_len = len(SYSTEM_PROMPT)
        history_len = sum(len(m.content) for m in request.history) if request.history else 0
        msg_len = len(request.message)
        total_chars = system_len + history_len + msg_len
        est_tokens = total_chars // 4
        
        llm_logger.info(f"Prompt Audit: Sys={system_len} chars, Hist={history_len} chars, Msg={msg_len} chars. Est tokens: {est_tokens}")
        
        # Automatically reduce if excessively large
        if est_tokens > 2000 and request.history:
            llm_logger.warning("Prompt excessively large. Truncating history.")
            request.history = request.history[-2:] # reduce to last 2
            
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if request.history:
            for msg in request.history[-4:]:
                messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": request.message})
        
        # Choose correct tool schema
        tools_schema = AVAILABLE_TOOLS_OLLAMA if ai_provider.provider_name() == "ollama" else OPENAI_TOOLS
        
        return await ai_provider.generate_response(
            messages=messages,
            settings=settings,
            execute_tool_cb=execute_tool,
            parse_text_tool_calls_cb=parse_text_tool_calls,
            sanitize_response_cb=sanitize_response,
            tools_schema=tools_schema,
            max_rounds=MAX_TOOL_ROUNDS,
            llm_logger=llm_logger,
            start_time=start_time,
            faq_cache_cb=lambda text: faq_cache.set(request.message.strip().lower(), text)
        )
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        status_code = getattr(e, 'status_code', getattr(e, 'status', 'N/A'))
        response_body = getattr(getattr(e, 'response', None), 'text', getattr(e, 'message', 'N/A'))
        
        error_msg = f"Exception Type: {type(e).__name__}\nHTTP Status: {status_code}\nProvider Response: {response_body}\nStack Trace:\n{tb}"
        llm_logger.error(f"Chat API Error Detailed Logging:\n{error_msg}")
        
        async def error_stream():
            yield f"The AI service encountered an issue. Please contact support. Error: {type(e).__name__}"
        return StreamingResponse(error_stream(), media_type="text/plain")
