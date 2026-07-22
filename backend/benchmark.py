"""
MediPrice Pro - AI Provider Benchmark Suite
Benchmarks Ollama, OpenRouter, and Gemini on:
  1. Response Quality (completeness, accuracy, formatting)
  2. Performance (latency, consistency)
  3. Reasoning and Tool Usage (correct tool selection, data interpretation)

Usage:
    cd backend
    python benchmark.py
"""

import httpx
import time
import os
import asyncio
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv, set_key

# Benchmark Questions (categorized)
BENCHMARK_QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is the market average price for CBC?",
        "category": "Data Retrieval",
        "expected_tool": "get_market_average",
        "difficulty": "Easy",
    },
    {
        "id": "Q2",
        "question": "Compare Vitamin D prices across all providers.",
        "category": "Data Retrieval",
        "expected_tool": "compare_tests",
        "difficulty": "Easy",
    },
    {
        "id": "Q3",
        "question": "Which tests are overpriced compared to the market? Show top 5.",
        "category": "Analysis",
        "expected_tool": "get_pricing_analysis",
        "difficulty": "Medium",
    },
    {
        "id": "Q4",
        "question": "If our CBC cost is Rs.200, calculate prices at 15% and 25% margins.",
        "category": "Calculation",
        "expected_tool": "calculate_margin",
        "difficulty": "Medium",
    },
    {
        "id": "Q5",
        "question": "Create a Women's Wellness Package with appropriate tests and 20% margin.",
        "category": "Package Creation",
        "expected_tool": "build_custom_package",
        "difficulty": "Hard",
    },
    {
        "id": "Q6",
        "question": "Compare CBC and HbA1c prices in Ahmedabad. Which one has better competitive positioning?",
        "category": "Business Intelligence",
        "expected_tool": "compare_tests",
        "difficulty": "Hard",
    },
    {
        "id": "Q7",
        "question": "What factors should we consider when setting prices for a new diagnostic test?",
        "category": "General Knowledge",
        "expected_tool": None,
        "difficulty": "Medium",
    },
]

PROVIDERS = ["ollama", "openrouter", "gemini"]

REPORT_DIR = Path(__file__).parent.parent
REPORT_PATH = REPORT_DIR / "benchmark_report.md"


def score_response(response_text, question_data):
    """Score a response on multiple dimensions (0-10 each)."""
    text = response_text.strip()
    text_lower = text.lower()

    # 1. Completeness
    completeness = 0
    if len(text) > 50:
        completeness += 3
    if len(text) > 150:
        completeness += 2
    if len(text) > 300:
        completeness += 2
    has_numbers = any(c.isdigit() for c in text)
    if has_numbers and question_data["expected_tool"]:
        completeness += 3
    elif not question_data["expected_tool"] and len(text) > 100:
        completeness += 3
    completeness = min(completeness, 10)

    # 2. Formatting Quality
    formatting = 0
    if "**" in text or "##" in text:
        formatting += 2
    if "|" in text and "---" in text:
        formatting += 3
    if "- " in text or "* " in text or any(str(i) + "." in text for i in range(1, 10)):
        formatting += 2
    if "price" in text_lower or "cost" in text_lower or "rs" in text_lower:
        formatting += 2
    if len(text) > 50:
        formatting += 1
    formatting = min(formatting, 10)

    # 3. Reasoning
    reasoning = 0
    reasoning_words = [
        "recommend", "suggest", "because", "therefore", "however",
        "competitive", "overpriced", "underpriced", "margin",
        "compared", "analysis", "insight", "strategy", "consider",
        "advantage", "opportunity", "should"
    ]
    matches = sum(1 for w in reasoning_words if w in text_lower)
    reasoning = min(matches * 2, 8)
    if len(text) > 200:
        reasoning += 2
    reasoning = min(reasoning, 10)

    # 4. Error Detection
    is_error = False
    error_markers = [
        "error", "unable to", "failed", "not found", "404", "500",
        "exception", "traceback", "[stream error"
    ]
    for marker in error_markers:
        if marker in text_lower:
            is_error = True
            break

    if is_error:
        completeness = max(completeness - 5, 0)
        reasoning = max(reasoning - 5, 0)

    overall = round((completeness + formatting + reasoning) / 3, 1)

    return {
        "completeness": completeness,
        "formatting": formatting,
        "reasoning": reasoning,
        "overall": overall,
        "is_error": is_error,
        "response_length": len(text),
    }


async def test_single_question(client, port, question_data):
    """Send a single question and measure everything."""
    start = time.time()
    try:
        response = await client.post(
            "http://localhost:" + str(port) + "/api/chat",
            json={"message": question_data["question"], "history": []},
        )
        elapsed = round(time.time() - start, 2)

        if response.status_code != 200:
            return {
                "elapsed": elapsed,
                "status": response.status_code,
                "response": "HTTP " + str(response.status_code) + ": " + response.text[:200],
                "scores": score_response("Error " + str(response.status_code), question_data),
                "success": False,
            }

        text = response.text
        scores = score_response(text, question_data)

        return {
            "elapsed": elapsed,
            "status": 200,
            "response": text,
            "scores": scores,
            "success": not scores["is_error"],
        }
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        return {
            "elapsed": elapsed,
            "status": 0,
            "response": "Connection Error: " + str(e),
            "scores": score_response("Error: " + str(e), question_data),
            "success": False,
        }


async def wait_for_server(port, timeout=30):
    """Wait for the server to be ready."""
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


async def run_benchmark():
    env_file = Path(__file__).parent / ".env"
    load_dotenv(env_file)
    original_provider = os.getenv("AI_PROVIDER", "ollama")

    all_results = {}
    port = 8001

    print("=" * 60)
    print("  MEDIPRICE PRO -- AI PROVIDER BENCHMARK")
    print("  Started: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("  Questions: " + str(len(BENCHMARK_QUESTIONS)))
    print("  Providers: " + ", ".join(p.upper() for p in PROVIDERS))
    print("=" * 60)

    for provider in PROVIDERS:
        print("")
        print("-" * 50)
        print("  TESTING: " + provider.upper())
        print("-" * 50)

        set_key(str(env_file), "AI_PROVIDER", provider)

        print("  Starting server on port " + str(port) + "...")
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api_server:app", "--port", str(port), "--host", "0.0.0.0"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(Path(__file__).parent),
        )

        ready = await wait_for_server(port, timeout=30)
        if not ready:
            print("  [X] Server failed to start for " + provider + ". Skipping.")
            proc.kill()
            all_results[provider] = None
            await asyncio.sleep(2)
            continue

        print("  [OK] Server ready. Running " + str(len(BENCHMARK_QUESTIONS)) + " questions...")
        print("")

        results = []
        async with httpx.AsyncClient(timeout=120.0) as client:
            for q in BENCHMARK_QUESTIONS:
                q_label = q["question"]
                if len(q_label) > 50:
                    q_label = q_label[:50] + "..."
                print("  [" + q["id"] + "] " + q_label, end=" ", flush=True)
                result = await test_single_question(client, port, q)
                results.append(result)

                icon = "[OK]" if result["success"] else "[FAIL]"
                print(icon + " " + str(result["elapsed"]) + "s  (score: " + str(result["scores"]["overall"]) + "/10)")

                await asyncio.sleep(2)

        all_results[provider] = results

        proc.kill()
        proc.wait()
        await asyncio.sleep(3)

    # Restore original provider
    set_key(str(env_file), "AI_PROVIDER", original_provider)

    # Generate report
    generate_report(all_results)

    # Restart original server
    print("")
    print("  Restoring AI_PROVIDER=" + original_provider + " and restarting server...")
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api_server:app", "--reload", "--port", "8000", "--host", "0.0.0.0"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=str(Path(__file__).parent),
    )
    print("  [OK] Benchmark complete! Report saved to: " + str(REPORT_PATH))


def generate_report(all_results):
    """Generate a comprehensive markdown benchmark report."""
    lines = []
    lines.append("# MediPrice Pro -- AI Provider Benchmark Report")
    lines.append("")
    lines.append("**Generated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("**Questions Tested:** " + str(len(BENCHMARK_QUESTIONS)))
    lines.append("**Providers:** " + ", ".join(p.upper() for p in PROVIDERS))
    lines.append("")

    # Executive Summary
    lines.append("---")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Metric | " + " | ".join(p.upper() for p in PROVIDERS) + " |")
    lines.append("|:-------|" + "|".join(":------:" for _ in PROVIDERS) + "|")

    summary = {}
    for provider in PROVIDERS:
        results = all_results.get(provider)
        if not results:
            summary[provider] = {
                "avg_time": "N/A", "success_rate": "N/A",
                "avg_quality": "N/A", "avg_reasoning": "N/A",
                "avg_formatting": "N/A", "avg_overall": "N/A",
                "fastest": "N/A", "slowest": "N/A",
            }
            continue

        times = [r["elapsed"] for r in results if r["success"]]
        qualities = [r["scores"]["completeness"] for r in results]
        reasonings = [r["scores"]["reasoning"] for r in results]
        formattings = [r["scores"]["formatting"] for r in results]
        overalls = [r["scores"]["overall"] for r in results]
        successes = sum(1 for r in results if r["success"])

        summary[provider] = {
            "avg_time": str(round(sum(times) / len(times), 1)) + "s" if times else "N/A",
            "fastest": str(round(min(times), 1)) + "s" if times else "N/A",
            "slowest": str(round(max(times), 1)) + "s" if times else "N/A",
            "success_rate": str(successes) + "/" + str(len(results)),
            "avg_quality": str(round(sum(qualities) / len(qualities), 1)) + "/10",
            "avg_reasoning": str(round(sum(reasonings) / len(reasonings), 1)) + "/10",
            "avg_formatting": str(round(sum(formattings) / len(formattings), 1)) + "/10",
            "avg_overall": str(round(sum(overalls) / len(overalls), 1)) + "/10",
        }

    metrics = [
        ("Avg Response Time", "avg_time"),
        ("Success Rate", "success_rate"),
        ("Quality Score", "avg_quality"),
        ("Reasoning Score", "avg_reasoning"),
        ("Formatting Score", "avg_formatting"),
        ("Overall Score", "avg_overall"),
    ]

    for label, key in metrics:
        row = "| " + label + " |"
        for p in PROVIDERS:
            row += " " + summary[p].get(key, "N/A") + " |"
        lines.append(row)

    # Performance Comparison
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Performance Comparison")
    lines.append("")
    lines.append("| Metric | " + " | ".join(p.upper() for p in PROVIDERS) + " |")
    lines.append("|:-------|" + "|".join(":------:" for _ in PROVIDERS) + "|")

    for label, key in [("Avg Latency", "avg_time"), ("Fastest", "fastest"), ("Slowest", "slowest")]:
        row = "| " + label + " |"
        for p in PROVIDERS:
            row += " " + summary[p].get(key, "N/A") + " |"
        lines.append(row)

    # Per-Question Detailed Results
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Results Per Question")
    lines.append("")

    for i, q in enumerate(BENCHMARK_QUESTIONS):
        lines.append("### " + q["id"] + ": " + q["question"])
        lines.append(
            "**Category:** " + q["category"]
            + " | **Difficulty:** " + q["difficulty"]
            + " | **Expected Tool:** `" + str(q["expected_tool"] or "None") + "`"
        )
        lines.append("")

        lines.append("| Provider | Time | Quality | Reasoning | Format | Overall | Status |")
        lines.append("|:---------|:-----|:--------|:----------|:-------|:--------|:-------|")

        for provider in PROVIDERS:
            results = all_results.get(provider)
            if not results:
                lines.append("| " + provider.upper() + " | N/A | N/A | N/A | N/A | N/A | Skipped |")
                continue

            r = results[i]
            s = r["scores"]
            status = "PASS" if r["success"] else "FAIL"
            lines.append(
                "| " + provider.upper()
                + " | " + str(r["elapsed"]) + "s"
                + " | " + str(s["completeness"]) + "/10"
                + " | " + str(s["reasoning"]) + "/10"
                + " | " + str(s["formatting"]) + "/10"
                + " | " + str(s["overall"]) + "/10"
                + " | " + status + " |"
            )

        lines.append("")
        lines.append("**Response Previews:**")
        lines.append("")
        for provider in PROVIDERS:
            results = all_results.get(provider)
            if not results:
                continue
            r = results[i]
            lines.append("<details><summary>" + provider.upper() + " (" + str(r["elapsed"]) + "s)</summary>")
            lines.append("")
            lines.append("```")
            lines.append(r["response"][:1500])
            lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")

        lines.append("")

    # Final Rankings
    lines.append("---")
    lines.append("")
    lines.append("## Final Rankings")
    lines.append("")

    rankings = []
    for provider in PROVIDERS:
        results = all_results.get(provider)
        if not results:
            continue

        overalls = [r["scores"]["overall"] for r in results]
        times = [r["elapsed"] for r in results if r["success"]]
        successes = sum(1 for r in results if r["success"])

        avg_score = sum(overalls) / len(overalls) if overalls else 0
        avg_time = sum(times) / len(times) if times else 999
        success_pct = (successes / len(results)) * 100 if results else 0

        speed_score = max(0, 10 - (avg_time / 3))
        final = (avg_score * 0.4) + (speed_score * 0.3) + ((success_pct / 10) * 0.3)

        rankings.append({
            "provider": provider.upper(),
            "avg_score": avg_score,
            "avg_time": avg_time,
            "speed_score": speed_score,
            "success_pct": success_pct,
            "final": round(final, 2),
        })

    rankings.sort(key=lambda x: x["final"], reverse=True)

    medals = ["1st", "2nd", "3rd"]
    lines.append("| Rank | Provider | Quality (40%) | Speed (30%) | Reliability (30%) | **Final Score** |")
    lines.append("|:-----|:---------|:-------------|:-----------|:-----------------|:---------------|")

    for i, r in enumerate(rankings):
        medal = medals[i] if i < 3 else ""
        lines.append(
            "| " + medal
            + " | **" + r["provider"] + "**"
            + " | " + str(round(r["avg_score"], 1)) + "/10"
            + " | " + str(round(r["speed_score"], 1)) + "/10"
            + " | " + str(round(r["success_pct"])) + "%"
            + " | **" + str(r["final"]) + "/10** |"
        )

    if rankings:
        winner = rankings[0]
        lines.append("")
        lines.append("### Winner: **" + winner["provider"] + "** with a final score of **" + str(winner["final"]) + "/10**")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Report generated automatically by MediPrice Pro Benchmark Suite.*")
    lines.append("")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("")
    print("=" * 60)
    print("  BENCHMARK RESULTS")
    print("=" * 60)
    if rankings:
        for i, r in enumerate(rankings):
            medal = medals[i] if i < 3 else " "
            line = "  " + medal + " " + r["provider"].ljust(12)
            line += " Score: " + str(r["final"]) + "/10"
            line += "  (Quality: " + str(round(r["avg_score"], 1))
            line += ", Speed: " + str(round(r["avg_time"], 1)) + "s)"
            print(line)
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
