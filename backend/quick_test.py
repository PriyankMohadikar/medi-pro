"""
Quick test: Verify OpenRouter and Gemini work with corrected model names.
Tests just 2 questions per provider to confirm connectivity.
"""

import httpx
import time
import os
import asyncio
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

QUICK_QUESTIONS = [
    {"id": "Q1", "question": "What is the market average price for CBC?"},
    {"id": "Q2", "question": "Which tests are overpriced?"},
]

PROVIDERS = ["openrouter", "gemini"]


async def wait_for_server(port, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get("http://localhost:" + str(port) + "/api/health")
                if r.status_code == 200:
                    return True
        except Exception:
            pass
        await asyncio.sleep(1)
    return False


async def run_quick_test():
    env_file = Path(__file__).parent / ".env"
    load_dotenv(env_file)
    original_provider = os.getenv("AI_PROVIDER", "ollama")
    port = 8001

    print("=" * 60)
    print("  QUICK CONNECTIVITY TEST")
    print("=" * 60)

    for provider in PROVIDERS:
        print("")
        print("--- TESTING: " + provider.upper() + " ---")

        set_key(str(env_file), "AI_PROVIDER", provider)

        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api_server:app", "--port", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(Path(__file__).parent),
        )

        ready = await wait_for_server(port)
        if not ready:
            print("  [X] Server failed to start.")
            proc.kill()
            continue

        print("  Server ready.")

        async with httpx.AsyncClient(timeout=120.0) as client:
            for q in QUICK_QUESTIONS:
                start = time.time()
                try:
                    r = await client.post(
                        "http://localhost:" + str(port) + "/api/chat",
                        json={"message": q["question"], "history": []},
                    )
                    elapsed = round(time.time() - start, 2)
                    text = r.text
                    is_error = "error" in text.lower()
                    icon = "[FAIL]" if is_error else "[OK]"
                    print("  " + q["id"] + " " + icon + " " + str(elapsed) + "s")
                    # Show first 200 chars of response
                    preview = text[:200].replace("\n", " ")
                    print("    -> " + preview)
                except Exception as e:
                    print("  " + q["id"] + " [ERROR] " + str(e))
                await asyncio.sleep(2)

        proc.kill()
        proc.wait()
        await asyncio.sleep(3)

    set_key(str(env_file), "AI_PROVIDER", original_provider)
    print("")
    print("  Done. AI_PROVIDER restored to: " + original_provider)


if __name__ == "__main__":
    asyncio.run(run_quick_test())
