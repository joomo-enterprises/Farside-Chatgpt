#!/usr/bin/env python3
"""
Episode 1: API Cost Calculator
Compare costs of OpenAI API vs self-hosted open-source models.

Usage:
    python 03_cost_calculator.py
    python 03_cost_calculator.py --daily-calls 1000 --users 100
"""

import argparse


# Pricing as of mid-2025 (approximate, per 1M tokens)
OPENAI_PRICING = {
    "GPT-4o": {"input": 2.50, "output": 10.00},
    "GPT-4o-mini": {"input": 0.15, "output": 0.60},
    "GPT-4-turbo": {"input": 10.00, "output": 30.00},
    "GPT-3.5-turbo": {"input": 0.50, "output": 1.50},
    "o1": {"input": 15.00, "output": 60.00},
    "o3": {"input": 10.00, "output": 40.00},
}

# Average tokens per call (rough estimate)
AVG_INPUT_TOKENS = 500
AVG_OUTPUT_TOKENS = 300


def calculate_openai_cost(model: str, daily_calls: int, days: int = 30) -> dict:
    """Calculate total cost for an OpenAI model."""
    pricing = OPENAI_PRICING[model]
    input_cost_per_call = (AVG_INPUT_TOKENS / 1_000_000) * pricing["input"]
    output_cost_per_call = (AVG_OUTPUT_TOKENS / 1_000_000) * pricing["output"]
    cost_per_call = input_cost_per_call + output_cost_per_call

    daily_cost = cost_per_call * daily_calls
    monthly_cost = daily_cost * days
    yearly_cost = daily_cost * 365

    return {
        "model": model,
        "cost_per_call": cost_per_call,
        "daily_cost": daily_cost,
        "monthly_cost": monthly_cost,
        "yearly_cost": yearly_cost,
    }


def calculate_self_hosted_cost(
    gpu_cost_monthly: float = 3.50, monthly_calls: int = 30_000
) -> dict:
    """Calculate cost for self-hosted model (GPU cost only)."""
    cost_per_call = gpu_cost_monthly / monthly_calls if monthly_calls > 0 else 0
    return {
        "model": "Self-hosted (Mistral/Llama/Gemma)",
        "cost_per_call": cost_per_call,
        "daily_cost": gpu_cost_monthly / 30,
        "monthly_cost": gpu_cost_monthly,
        "yearly_cost": gpu_cost_monthly * 12,
    }


def print_comparison(daily_calls: int, users: int):
    """Print a full cost comparison table."""
    total_daily = daily_calls * users

    print("=" * 70)
    print("  API Cost Calculator — On The FarSide Series, Episode 1")
    print("=" * 70)
    print(f"\n  Assumptions:")
    print(f"    Daily API calls per user: {daily_calls:,}")
    print(f"    Number of users: {users:,}")
    print(f"    Total daily calls: {total_daily:,}")
    print(f"    Avg input tokens per call: {AVG_INPUT_TOKENS:,}")
    print(f"    Avg output tokens per call: {AVG_OUTPUT_TOKENS:,}")
    print(f"    Self-hosted GPU: $3.50/month (e.g. RTX 4090 or T4 on cloud)")

    print(f"\n{'Model':<25} {'Per Call':>10} {'Daily':>10} {'Monthly':>12} {'Yearly':>12}")
    print("-" * 70)

    results = []
    for model in OPENAI_PRICING:
        r = calculate_openai_cost(model, total_daily)
        results.append(r)
        print(
            f"{r['model']:<25} ${r['cost_per_call']:>8.4f} ${r['daily_cost']:>8.2f} "
            f"${r['monthly_cost']:>10.2f} ${r['yearly_cost']:>10.2f}"
        )

    # Self-hosted
    monthly_calls = total_daily * 30
    r = calculate_self_hosted_cost(3.50, monthly_calls)
    results.append(r)
    print(
        f"{r['model']:<25} ${r['cost_per_call']:>8.6f} ${r['daily_cost']:>8.2f} "
        f"${r['monthly_cost']:>10.2f} ${r['yearly_cost']:>10.2f}"
    )

    print("-" * 70)

    # Savings calculation
    gpt4o = results[0]  # GPT-4o
    self_hosted = results[-1]
    monthly_savings = gpt4o["monthly_cost"] - self_hosted["monthly_cost"]
    yearly_savings = gpt4o["yearly_cost"] - self_hosted["yearly_cost"]

    print(f"\n  Monthly savings vs GPT-4o: ${monthly_savings:,.2f}")
    print(f"  Yearly savings vs GPT-4o:  ${yearly_savings:,.2f}")
    print(f"\n  Self-hosted = one-time hardware cost + electricity.")
    print(f"  Your data stays YOURS. No API calls. No rate limits.")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="API Cost Calculator")
    parser.add_argument(
        "--daily-calls", type=int, default=100, help="Daily API calls per user"
    )
    parser.add_argument("--users", type=int, default=10, help="Number of users")
    args = parser.parse_args()

    print_comparison(args.daily_calls, args.users)


if __name__ == "__main__":
    main()
