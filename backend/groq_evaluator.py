import asyncio
import httpx
import time
import json
import re
from pathlib import Path

PROMPTS = [
    "Compare CBC prices",
    "Compare Vitamin D prices",
    "Suggest Women's Wellness Package",
    "Suggest Men's Wellness Package",
    "Suggest Senior Citizen Package",
    "Suggest Fitness Package",
    "Suggest Executive Package",
    "Suggest Package under ₹3000",
    "Suggest Package under ₹5000",
    "Calculate 20% Margin",
    "Calculate 15% Margin",
    "Recommend Competitive Pricing",
    "Suggest Patient Retention Strategy",
    "Suggest Healthcare Marketing Strategy",
    "Suggest Festival Offers",
    "Identify Overpriced Tests",
    "Identify Underpriced Tests",
    "Compare Competitor Packages",
    "Recommend Package Improvements",
    "Explain Why a Test is Overpriced",
    "Recommend Bundle Strategy",
    "Suggest Cross-selling Opportunities",
    "Suggest Upselling Opportunities",
    "Generate Business Insights",
    "Recommend Pricing Strategy for Ahmedabad",
    "Recommend Corporate Wellness Package"
]

ROUNDS = 3
API_URL = "http://localhost:8000/api/chat"
LOG_FILE = Path(__file__).parent / "logs" / "llm.log"

async def tail_log_for_stats(start_timestamp):
    """Read the log file from bottom up to find the most recent DEBUG_MODE_STATS after the request."""
    if not LOG_FILE.exists():
        return None
        
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in reversed(lines):
            if "DEBUG_MODE_STATS:" in line:
                try:
                    json_str = line.split("DEBUG_MODE_STATS:")[1].strip()
                    stats = json.loads(json_str)
                    return stats
                except:
                    continue
    except Exception as e:
        print(f"Log parsing error: {e}")
    return None

async def run_evaluation():
    print(f"Starting Groq Evaluation: {len(PROMPTS)} prompts x {ROUNDS} rounds")
    
    results = []
    
    async with httpx.AsyncClient(timeout=300) as client:
        for r in range(ROUNDS):
            print(f"\n--- ROUND {r+1} ---")
            for i, prompt in enumerate(PROMPTS):
                safe_prompt = prompt.encode('ascii', 'replace').decode()
                print(f"Testing [{i+1}/{len(PROMPTS)}]: {safe_prompt}")
                
                req_start = time.time()
                success = False
                response_text = ""
                latency = 0
                
                try:
                    # Time to First Byte (approximate warm/cold start)
                    ttfb = 0
                    first_chunk = True
                    
                    async with client.stream("POST", API_URL, json={"message": prompt}) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_text():
                            if first_chunk:
                                ttfb = time.time() - req_start
                                first_chunk = False
                            response_text += chunk
                            
                    latency = time.time() - req_start
                    success = True
                except Exception as e:
                    print(f"  [ERROR] Request failed: {e}")
                    response_text = f"ERROR: {str(e)}"
                    latency = time.time() - req_start
                
                # Give a small delay to ensure logs are flushed
                await asyncio.sleep(1)
                
                stats = await tail_log_for_stats(req_start)
                
                result_entry = {
                    "round": r + 1,
                    "prompt": prompt,
                    "success": success,
                    "latency": latency,
                    "ttfb": ttfb if success else 0,
                    "response_length": len(response_text),
                    "response": response_text,
                    "stats": stats
                }
                
                results.append(result_entry)
                print(f"  Latency: {latency:.2f}s | TTFB: {ttfb:.2f}s | Length: {len(response_text)} chars")
                
                # Sleep a bit to avoid hitting rate limits too fast (Groq has RPM limits)
                await asyncio.sleep(3)
                
    # Save results
    out_path = Path(__file__).parent / "groq_eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\nEvaluation Complete! Results saved to {out_path}")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
