"""
Episode 1: API Cost Calculator
Compare costs of proprietary APIs vs self-hosted open-source models.

From Episode 1 of On The FarSide Series.
"""

# Pricing as of 2025 (per 1K tokens)
PRICING = {
    "GPT-4o": {
        "input": 0.005,
        "output": 0.015,
        "type": "proprietary",
        "url": "https://openai.com/pricing",
    },
    "GPT-4o-mini": {
        "input": 0.00015,
        "output": 0.0006,
        "type": "proprietary",
        "url": "https://openai.com/pricing",
    },
    "Claude Opus 4.1": {
        "input": 0.015,
        "output": 0.075,
        "type": "proprietary",
        "url": "https://anthropic.com/pricing",
    },
    "Gemini 2.5 Pro": {
        "input": 0.00125,
        "output": 0.005,
        "type": "proprietary",
        "url": "https://ai.google.dev/pricing",
    },
    "Mistral 7B (local)": {
        "input": 0.0,
        "output": 0.0,
        "type": "open-source",
        "url": "https://ollama.ai",
    },
    "LLaMA 4 Scout (local)": {
        "input": 0.0,
        "output": 0.0,
        "type": "open-source",
        "url": "https://ollama.ai",
    },
    "Gemma 3 (local)": {
        "input": 0.0,
        "output": 0.0,
        "type": "open-source",
        "url": "https://ollama.ai",
    },
}

# Average tokens per API call (typical conversation)
AVG_INPUT_TOKENS = 500
AVG_OUTPUT_TOKENS = 300


def calculate_monthly_cost(model: str, calls_per_day: int, days: int = 30) -> dict:
    """Calculate monthly cost for a given model and usage."""
    pricing = PRICING[model]
    total_input_tokens = calls_per_day * AVG_INPUT_TOKENS * days
    total_output_tokens = calls_per_day * AVG_OUTPUT_TOKENS * days

    input_cost = (total_input_tokens / 1000) * pricing["input"]
    output_cost = (total_output_tokens / 1000) * pricing["output"]
    total = input_cost + output_cost

    return {
        "model": model,
        "calls_per_day": calls_per_day,
        "days": days,
        "total_calls": calls_per_day * days,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total,
        "type": pricing["type"],
    }


def print_comparison(calls_per_day: int):
    """Print a cost comparison table."""
    print()
    print("=" * 70)
    print(f"  Monthly Cost Comparison — {calls_per_day} API calls/day")
    print(f"  ({calls_per_day * 30:,} calls/month, ~{AVG_INPUT_TOKENS}+{AVG_OUTPUT_TOKENS} tokens/call)")
    print("=" * 70)
    print()
    print(f"{'Model':<25} {'Type':<14} {'Input':>10} {'Output':>10} {'Total':>10}")
    print("-" * 70)

    proprietary_total = 0
    for model, info in PRICING.items():
        result = calculate_monthly_cost(model, calls_per_day)
        print(
            f"{model:<25} {info['type']:<14} "
            f"${result['input_cost']:>8.2f} "
            f"${result['output_cost']:>8.2f} "
            f"${result['total_cost']:>8.2f}"
        )
        if info["type"] == "proprietary":
            proprietary_total = result["total_cost"]

    print("-" * 70)
    print()
    print("  Open-source cost = $0.00 per call (you pay for hardware only)")
    print()

    # Savings calculation
    cheapest_proprietary = min(
        calculate_monthly_cost(m, calls_per_day)["total_cost"]
        for m, info in PRICING.items()
        if info["type"] == "proprietary"
    )
    if cheapest_proprietary > 0:
        print(f"  💰 Savings with open-source: ${cheapest_proprietary:.2f}/month")
        print(f"  💰 Annual savings: ${cheapest_proprietary * 12:.2f}/year")
        if calls_per_day >= 100:
            most_expensive = max(
                calculate_monthly_cost(m, calls_per_day)["total_cost"]
                for m, info in PRICING.items()
                if info["type"] == "proprietary"
            )
            print(f"  💰 vs most expensive (Claude Opus): ${most_expensive:.2f}/month")
            print(f"  💰 Annual savings vs Claude: ${most_expensive * 12:.2f}/year")
    print()


def main():
    """Run the cost calculator."""
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║  On The FarSide Series — Episode 1              ║")
    print("║  API Cost Calculator: Proprietary vs Open Source ║")
    print("╚══════════════════════════════════════════════════╝")

    scenarios = [10, 100, 1000, 10000]

    for calls in scenarios:
        print_comparison(calls)

    print("=" * 70)
    print("  NOTES:")
    print("  • Open-source: $0 API cost. You pay for hardware/cloud instance.")
    print("  • A used GPU server: ~$500 one-time or ~$5-15/month cloud.")
    print("  • Proprietary: costs scale linearly with usage. Forever.")
    print("  • Prices subject to change. Check provider websites for updates.")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
