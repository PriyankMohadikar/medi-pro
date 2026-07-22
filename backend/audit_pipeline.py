import asyncio
import os
import sys
import json
import httpx

sys.path.append(os.path.dirname(__file__))

from config import load_settings
import chat_services

async def test_postgres_functions():
    print("========================================")
    print("[1/3] Auditing PostgreSQL Functions")
    print("========================================")
    
    try:
        res = chat_services.get_market_average("Vitamin D")
        print("[PASS] get_market_average passed")
    except Exception as e:
        print(f"[FAIL] get_market_average failed: {e}")
        
    try:
        res = chat_services.compare_tests(["CBC", "Lipid Profile"])
        print("[PASS] compare_tests passed")
    except Exception as e:
        print(f"[FAIL] compare_tests failed: {e}")
        
    try:
        res = chat_services.compare_packages(["Basic Health Checkup"])
        print("[PASS] compare_packages passed")
    except Exception as e:
        print(f"[FAIL] compare_packages failed: {e}")
        
    try:
        res = chat_services.calculate_margin(1000, 20)
        print("[PASS] calculate_margin passed")
    except Exception as e:
        print(f"[FAIL] calculate_margin failed: {e}")
        
    try:
        res = chat_services.build_custom_package(["CBC", "ESR"], 15)
        print("[PASS] build_custom_package passed")
    except Exception as e:
        print(f"[FAIL] build_custom_package failed: {e}")
        
    try:
        res = chat_services.get_pricing_analysis()
        print("[PASS] get_pricing_analysis passed")
    except Exception as e:
        print(f"[FAIL] get_pricing_analysis failed: {e}")


async def test_openrouter():
    print("\n========================================")
    print("[2/3] Verifying OpenRouter Connectivity")
    print("========================================")
    settings = load_settings()
    import openai
    client = openai.AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
    try:
        response = await client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print(f"[PASS] API works. Model ({response.model}) responded.")
    except Exception as e:
        print(f"[FAIL] API connectivity failed: {e}")


async def test_chat_api():
    print("\n========================================")
    print("[3/3] Validating 7 Required Prompts")
    print("========================================")
    prompts = [
        "Compare Vitamin D prices",
        "Compare CBC",
        "Suggest Women's Package",
        "20% Margin",
        "Package under 3000 INR",
        "Business Strategy",
        "Pricing Recommendation"
    ]
    async with httpx.AsyncClient(timeout=180) as client:
        for p in prompts:
            try:
                response = await client.post(
                    "http://localhost:8000/api/chat",
                    json={"message": p, "history": []}
                )
                if response.status_code == 200:
                    text = response.text
                    if "Error:" in text or "issue" in text.lower():
                        print(f"[FAIL] Prompt '{p}' returned an error message in body: {text[:50]}...")
                    else:
                        print(f"[PASS] Prompt '{p}' returned 200 OK ({len(text)} chars)")
                else:
                    print(f"[FAIL] Prompt '{p}' failed with {response.status_code}: {response.text}")
            except Exception as e:
                print(f"[FAIL] Prompt '{p}' request failed: {e}")


async def main():
    await test_postgres_functions()
    await test_openrouter()
    await test_chat_api()

if __name__ == "__main__":
    asyncio.run(main())
