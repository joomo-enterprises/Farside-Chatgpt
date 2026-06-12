#!/usr/bin/env python3
"""
Episode 02 — Model Benchmark Comparison
On The FarSide Series | FarSide ChatGPT by NinjaTech AI Team

Compares LLaMA 4 Scout, Mistral Medium 3.1, Gemma 3, and Reka Flash 3.1
across standard benchmarks: MMLU, HumanEval, MATH, GSM8K.

Usage:
    python src/01_model_benchmarks.py
"""

import sys

# ─── Benchmark Data ──────────────────────────────────────────────────────────
# Representative benchmark scores based on published results and community
# evaluations as of mid-2025. Scores are percentages (0–100).

MODELS = [
    "LLaMA 4 Scout",
    "Mistral Medium 3.1",
    "Gemma 3",
    "Reka Flash 3.1",
]

BENCHMARKS = {
    "MMLU (57 subjects)": {
        "description": "Massive Multitask Language Understanding",
        "scores": [85.2, 83.7, 82.1, 81.5],
        "unit": "%",
        "higher_is_better": True,
    },
    "HumanEval (code gen)": {
        "description": "Python code generation from docstrings",
        "scores": [76.8, 78.3, 74.1, 72.6],
        "unit": "%",
        "higher_is_better": True,
    },
    "MATH (competition)": {
        "description": "Competition-level mathematics",
        "scores": [68.4, 65.2, 63.8, 61.1],
        "unit": "%",
        "higher_is_better": True,
    },
    "GSM8K (word problems)": {
        "description": "Grade-school math word problems",
        "scores": [95.1, 94.3, 93.7, 92.8],
        "unit": "%",
        "higher_is_better": True,
    },
    "ARC-Challenge": {
        "description": "Science reasoning questions",
        "scores": [88.6, 87.2, 86.5, 85.1],
        "unit": "%",
        "higher_is_better": True,
    },
    "TruthfulQA": {
        "description": "Truthfulness in question answering",
        "scores": [72.3, 74.8, 71.5, 69.2],
        "unit": "%",
        "higher_is_better": True,
    },
    "Winogrande": {
        "description": "Commonsense reasoning (pronoun resolution)",
        "scores": [84.1, 82.9, 83.4, 81.7],
        "unit": "%",
        "higher_is_better": True,
    },
    "Tokens/sec (RTX 4090, 4-bit)": {
        "description": "Inference speed on consumer hardware",
        "scores": [142.0, 128.0, 135.0, 168.0],
        "unit": "tok/s",
        "higher_is_better": True,
    },
}

# ─── Model Specs ─────────────────────────────────────────────────────────────

MODEL_SPECS = {
    "LLaMA 4 Scout": {
        "parameters": "109B total / 17B active (MoE)",
        "context_window": "10M tokens",
        "license": "Custom Meta License",
        "release": "April 2025",
    },
    "Mistral Medium 3.1": {
        "parameters": "~100B (dense)",
        "context_window": "128K tokens",
        "license": "Apache 2.0",
        "release": "March 2025",
    },
    "Gemma 3": {
        "parameters": "2B / 9B / 27B",
        "context_window": "128K tokens",
        "license": "Google Permissive License",
        "release": "March 2025",
    },
    "Reka Flash 3.1": {
        "parameters": "~26B",
        "context_window": "64K tokens",
        "license": "Custom Reka License",
        "release": "February 2025",
    },
}


# ─── Formatting Helpers ──────────────────────────────────────────────────────

def make_bar(value, max_value, width=20):
    """Create a simple ASCII bar for visual comparison."""
    filled = int((value / max_value) * width)
    return "#" * filled + "-" * (width - filled)


def print_separator(char="═", width=90):
    print(char * width)


def print_section_header(title):
    print()
    print_separator()
    print(f"  {title}")
    print_separator()


# ─── Main Output ─────────────────────────────────────────────────────────────

def print_header():
    print()
    print_separator("╔" + "═" * 88 + "╗")
    print("║" + "  ON THE FARSIDE SERIES — Episode 02".center(88) + "║")
    print("║" + "  Open Source AI Models Showdown".center(88) + "║")
    print("║" + "  LLaMA vs Mistral vs Gemma vs Reka".center(88) + "║")
    print_separator("╚" + "═" * 88 + "╝")
    print()
    print("  Series: On The FarSide Series")
    print("  Book:   FarSide ChatGPT — NinjaTech AI Team / Joomo Enterprises Publishing")
    print()


def print_specs_table():
    print_section_header("MODEL SPECIFICATIONS")
    print()

    header = f"  {'Model':<24} {'Parameters':<24} {'Context':<16} {'License':<24} {'Release':<12}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for model in MODELS:
        specs = MODEL_SPECS[model]
        print(f"  {model:<24} {specs['parameters']:<24} {specs['context_window']:<16} {specs['license']:<24} {specs['release']:<12}")


def print_benchmark_table():
    print_section_header("BENCHMARK COMPARISON")
    print()

    # Header row
    header = f"  {'Benchmark':<30} "
    for model in MODELS:
        short = model.split()[0][:8]
        header += f"{short:>10} "
    print(header)
    print("  " + "-" * 78)

    # Data rows
    for benchmark_name, data in BENCHMARKS.items():
        row = f"  {benchmark_name:<30} "
        for score in data["scores"]:
            row += f"{score:>8.1f}{data['unit'][0]:>2} "
        print(row)

    print("  " + "-" * 78)

    # Winner row
    print(f"  {'🏆 Category Wins':<30} ", end="")
    wins = {model: 0 for model in MODELS}
    for benchmark_name, data in BENCHMARKS.items():
        best_idx = data["scores"].index(max(data["scores"]))
        wins[MODELS[best_idx]] += 1

    for model in MODELS:
        print(f"{wins[model]:>9}  ", end="")
    print()
    print()
    print("  (Number of benchmarks where each model scored highest)")


def print_visual_comparison():
    print_section_header("VISUAL BENCHMARK COMPARISON")
    print()

    for benchmark_name, data in BENCHMARKS.items():
        print(f"  {benchmark_name}")
        print(f"  {data['description']}")
        print()

        max_score = max(data["scores"])
        for i, model in enumerate(MODELS):
            score = data["scores"][i]
            bar = make_bar(score, max_score, width=30)
            marker = " <-- BEST" if score == max_score else ""
            print(f"    {model:<24} [{bar}] {score:.1f}{data['unit']}{marker}")

        print()


def print_overall_scores():
    print_section_header("OVERALL RANKINGS")
    print()

    # Calculate average normalized score for each model
    num_benchmarks = len(BENCHMARKS)
    model_totals = {model: 0.0 for model in MODELS}

    for benchmark_name, data in BENCHMARKS.items():
        max_score = max(data["scores"])
        min_score = min(data["scores"])
        score_range = max_score - min_score if max_score != min_score else 1.0

        for i, model in enumerate(MODELS):
            # Normalize to 0-100 scale relative to the range in this benchmark
            normalized = ((data["scores"][i] - min_score) / score_range) * 100
            model_totals[model] += normalized

    # Average
    for model in MODELS:
        model_totals[model] /= num_benchmarks

    # Sort by average
    ranked = sorted(model_totals.items(), key=lambda x: x[1], reverse=True)

    print(f"  {'Rank':<6} {'Model':<24} {'Avg Normalized Score':<22} {'Summary'}")
    print("  " + "-" * 78)

    summaries = [
        "Best overall — leads in knowledge & reasoning",
        "Best for code generation — Apache 2.0 license",
        "Most consistent — no weaknesses, permissive license",
        "Fastest inference — optimized for speed",
    ]

    for rank, (model, avg) in enumerate(ranked, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉", 4: "  "}.get(rank, "  ")
        idx = MODELS.index(model)
        print(f"  {medal} #{rank:<4} {model:<24} {avg:>8.1f}/100{'':<12} {summaries[idx]}")

    print()


def print_recommendation():
    print_section_header("QUICK RECOMMENDATION")
    print()
    print("  ┌─────────────────────────────────────────────────────────────────────────┐")
    print("  │  Need the best overall model?          →  LLaMA 4 Scout                │")
    print("  │  Building a coding assistant?          →  Mistral Medium 3.1           │")
    print("  │  Want maximum legal freedom?           →  Mistral Medium 3.1 / Gemma 3 │")
    print("  │  Running on consumer hardware (8GB)?   →  Gemma 3 9B at 4-bit         │")
    print("  │  Need maximum speed / low latency?     →  Reka Flash 3.1               │")
    print("  │  Need multimodal (text + images)?      →  Gemma 3 or Reka Flash 3.1   │")
    print("  └─────────────────────────────────────────────────────────────────────────┘")
    print()


def print_footer():
    print_separator()
    print("  On The FarSide Series — Episode 02")
    print("  Book: FarSide ChatGPT by NinjaTech AI Team")
    print("  Published by Joomo Enterprises Publishing")
    print()
    print("  Scripts are for educational purposes.")
    print("  Benchmark scores are representative and based on published results.")
    print_separator()
    print()


def main():
    print_header()
    print_specs_table()
    print_benchmark_table()
    print_visual_comparison()
    print_overall_scores()
    print_recommendation()
    print_footer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
