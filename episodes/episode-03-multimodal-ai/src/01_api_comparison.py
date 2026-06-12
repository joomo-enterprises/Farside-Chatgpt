#!/usr/bin/env python3
"""
Episode 03: Multimodal AI - API Pricing Comparison
On The FarSide Series

Compares API pricing for multimodal capabilities across:
- OpenAI GPT-4o
- Google Gemini 2.5 Pro
- Anthropic Claude Opus 4.1

Pricing as of mid-2025. Always check official docs for latest rates.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelPricing:
    """Stores pricing info for a single model."""
    name: str
    provider: str
    # Text pricing (per 1M tokens)
    text_input_per_1m: float
    text_output_per_1m: float
    # Image pricing
    image_input_per_1m: float  # tokenized, per 1M tokens
    image_tokens_estimate: int  # approximate tokens per image
    # Audio pricing (per 1M tokens)
    audio_input_per_1m: Optional[float] = None
    audio_output_per_1m: Optional[float] = None
    audio_seconds_per_1k_tokens: Optional[float] = None
    # Context window
    context_window: int = 128_000
    # Tiered pricing threshold (Gemini has cheaper first 200K)
    tier_threshold: Optional[int] = None
    tier2_text_input_per_1m: Optional[float] = None

    def text_input_cost(self, tokens: int) -> float:
        """Calculate text input cost with tiered pricing support."""
        if self.tier_threshold and self.tier2_text_input_per_1m:
            if tokens <= self.tier_threshold:
                return (tokens / 1_000_000) * self.text_input_per_1m
            else:
                base = (self.tier_threshold / 1_000_000) * self.text_input_per_1m
                extra = ((tokens - self.tier_threshold) / 1_000_000) * self.tier2_text_input_per_1m
                return base + extra
        return (tokens / 1_000_000) * self.text_input_per_1m

    def text_output_cost(self, tokens: int) -> float:
        """Calculate text output cost."""
        return (tokens / 1_000_000) * self.text_output_per_1m

    def image_cost(self, num_images: int = 1) -> float:
        """Calculate image input cost."""
        total_tokens = num_images * self.image_tokens_estimate
        return (total_tokens / 1_000_000) * self.image_input_per_1m

    def audio_input_cost(self, seconds: float) -> Optional[float]:
        """Calculate audio input cost from duration in seconds."""
        if self.audio_input_per_1m is None or self.audio_seconds_per_1k_tokens is None:
            return None
        tokens = (seconds / self.audio_seconds_per_1k_tokens) * 1000
        return (tokens / 1_000_000) * self.audio_input_per_1m

    def audio_output_cost(self, seconds: float) -> Optional[float]:
        """Calculate audio output cost from duration in seconds."""
        if self.audio_output_per_1m is None or self.audio_seconds_per_1k_tokens is None:
            return None
        tokens = (seconds / self.audio_seconds_per_1k_tokens) * 1000
        return (tokens / 1_000_000) * self.audio_output_per_1m


# --- Model Definitions ---

GPT4O = ModelPricing(
    name="GPT-4o",
    provider="OpenAI",
    text_input_per_1m=2.50,
    text_output_per_1m=10.00,
    image_input_per_1m=2.50,  # same as text input
    image_tokens_estimate=1000,
    audio_input_per_1m=100.00,
    audio_output_per_1m=200.00,
    audio_seconds_per_1k_tokens=25.0,  # ~25 seconds per 1K tokens
    context_window=128_000,
)

GEMINI = ModelPricing(
    name="Gemini 2.5 Pro",
    provider="Google DeepMind",
    text_input_per_1m=1.25,
    text_output_per_1m=10.00,
    image_input_per_1m=1.25,  # same as text input
    image_tokens_estimate=1000,
    audio_input_per_1m=0.50,
    audio_output_per_1m=None,  # audio output via different endpoint
    audio_seconds_per_1k_tokens=8.0,  # ~8 seconds per 1K tokens
    context_window=2_000_000,
    tier_threshold=200_000,
    tier2_text_input_per_1m=2.50,
)

CLAUDE = ModelPricing(
    name="Claude Opus 4.1",
    provider="Anthropic",
    text_input_per_1m=15.00,
    text_output_per_1m=75.00,
    image_input_per_1m=15.00,  # same as text input
    image_tokens_estimate=1250,  # slightly higher due to resolution
    audio_input_per_1m=None,  # no native audio API
    audio_output_per_1m=None,
    audio_seconds_per_1k_tokens=None,
    context_window=200_000,
)


def print_header(title: str, width: int = 70):
    """Print a formatted section header."""
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_subheader(title: str, width: int = 70):
    """Print a formatted subsection header."""
    print()
    print(f"  --- {title} ---")
    print("-" * width)


def format_cost(cost: float) -> str:
    """Format cost with appropriate precision."""
    if cost < 0.01:
        return f"${cost:.6f}"
    elif cost < 1.0:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"


def compare_text_pricing(models: list, input_tokens: int, output_tokens: int):
    """Compare text pricing across models."""
    print_subheader(
        f"Text Pricing: {input_tokens:,} input tokens + {output_tokens:,} output tokens"
    )
    print(f"  {'Model':<25} {'Input Cost':>12} {'Output Cost':>12} {'Total':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*12}")

    for m in models:
        inp = m.text_input_cost(input_tokens)
        out = m.text_output_cost(output_tokens)
        total = inp + out
        print(f"  {m.name:<25} {format_cost(inp):>12} {format_cost(out):>12} {format_cost(total):>12}")


def compare_image_pricing(models: list, num_images: int):
    """Compare image pricing across models."""
    print_subheader(f"Image Pricing: {num_images} image(s)")
    print(f"  {'Model':<25} {'Est. Tokens':>12} {'Cost':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12}")

    for m in models:
        tokens = num_images * m.image_tokens_estimate
        cost = m.image_cost(num_images)
        print(f"  {m.name:<25} {tokens:>12,} {format_cost(cost):>12}")


def compare_audio_pricing(models: list, duration_seconds: float):
    """Compare audio pricing across models."""
    minutes = duration_seconds / 60
    print_subheader(f"Audio Pricing: {duration_seconds:.0f} seconds ({minutes:.1f} min)")
    print(f"  {'Model':<25} {'Input Cost':>12} {'Output Cost':>12} {'Total':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*12}")

    for m in models:
        inp = m.audio_input_cost(duration_seconds)
        out = m.audio_output_cost(duration_seconds)
        if inp is None:
            print(f"  {m.name:<25} {'N/A':>12} {'N/A':>12} {'N/A':>12}")
        else:
            total = inp + (out or 0)
            out_str = format_cost(out) if out else "N/A"
            print(f"  {m.name:<25} {format_cost(inp):>12} {out_str:>12} {format_cost(total):>12}")


def compare_monthly_projection(models: list, requests_per_day: int,
                                input_tokens: int, output_tokens: int,
                                images_per_request: int, audio_seconds_per_request: float):
    """Compare monthly cost projection."""
    days = 30
    total_requests = requests_per_day * days

    print_subheader(
        f"Monthly Projection: {requests_per_day:,} requests/day × {days} days = {total_requests:,} requests"
    )
    print(f"  Each request: {input_tokens:,} in + {output_tokens:,} out + "
          f"{images_per_request} image(s) + {audio_seconds_per_request:.0f}s audio")
    print()

    print(f"  {'Model':<25} {'Text Cost':>12} {'Image Cost':>12} {'Audio Cost':>12} {'TOTAL':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")

    for m in models:
        text_total = (m.text_input_cost(input_tokens) + m.text_output_cost(output_tokens)) * total_requests
        img_total = m.image_cost(images_per_request) * total_requests
        audio_in = m.audio_input_cost(audio_seconds_per_request) or 0
        audio_out = m.audio_output_cost(audio_seconds_per_request) or 0
        audio_total = (audio_in + audio_out) * total_requests
        grand_total = text_total + img_total + audio_total

        audio_str = format_cost(audio_total) if audio_total > 0 else "N/A"
        print(f"  {m.name:<25} {format_cost(text_total):>12} {format_cost(img_total):>12} "
              f"{audio_str:>12} {format_cost(grand_total):>12}")


def compare_per_minute_audio(models: list):
    """Show cost per minute of audio for each model."""
    print_subheader("Audio Cost Per Minute")
    print(f"  {'Model':<25} {'Input/min':>12} {'Output/min':>12} {'Round-trip/min':>15}")
    print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*15}")

    for m in models:
        inp = m.audio_input_cost(60.0)
        out = m.audio_output_cost(60.0)
        if inp is None:
            print(f"  {m.name:<25} {'N/A':>12} {'N/A':>12} {'N/A':>15}")
        else:
            total = inp + (out or 0)
            out_str = format_cost(out) if out else "N/A"
            total_str = format_cost(total) if out else format_cost(inp) + "+"
            print(f"  {m.name:<25} {format_cost(inp):>12} {out_str:>12} {total_str:>15}")


def main():
    models = [GPT4O, GEMINI, CLAUDE]

    print()
    print("  ╔══════════════════════════════════════════════════════════════════════╗")
    print("  ║       MULTIMODAL AI API PRICING COMPARISON                          ║")
    print("  ║       GPT-4o vs Gemini 2.5 Pro vs Claude Opus 4.1                  ║")
    print("  ║       On The FarSide Series — Episode 03                            ║")
    print("  ╚══════════════════════════════════════════════════════════════════════╝")

    # --- Per-1M Token Pricing Table ---
    print_header("BASE PRICING (per 1 million tokens)")
    print()
    print(f"  {'Model':<25} {'Provider':<18} {'Text In':>10} {'Text Out':>10} {'Context':>12}")
    print(f"  {'-'*25} {'-'*18} {'-'*10} {'-'*10} {'-'*12}")
    for m in models:
        ctx = f"{m.context_window:,}"
        if m.context_window >= 1_000_000:
            ctx = f"{m.context_window // 1_000_000}M"
        elif m.context_window >= 1_000:
            ctx = f"{m.context_window // 1_000}K"
        tier_note = ""
        if m.tier_threshold:
            tier_note = f" (first {m.tier_threshold // 1_000}K)"
        print(f"  {m.name:<25} {m.provider:<18} ${m.text_input_per_1m:>8.2f}{tier_note} ${m.text_output_per_1m:>8.2f} {ctx:>12}")

    # --- Text Pricing Scenarios ---
    print_header("TEXT PRICING SCENARIOS")
    compare_text_pricing(models, 1_000, 500)
    compare_text_pricing(models, 10_000, 2_000)
    compare_text_pricing(models, 100_000, 10_000)
    compare_text_pricing(models, 500_000, 50_000)

    # --- Image Pricing ---
    print_header("IMAGE PRICING")
    compare_image_pricing(models, 1)
    compare_image_pricing(models, 5)
    compare_image_pricing(models, 10)

    # --- Audio Pricing ---
    print_header("AUDIO PRICING")
    compare_audio_pricing(models, 30)     # 30 seconds
    compare_audio_pricing(models, 60)     # 1 minute
    compare_audio_pricing(models, 300)    # 5 minutes
    compare_per_minute_audio(models)

    # --- Monthly Projections ---
    print_header("MONTHLY COST PROJECTIONS")

    # Scenario 1: Light multimodal app
    print_subheader("Scenario 1: Light Multimodal App")
    compare_monthly_projection(models,
                               requests_per_day=1_000,
                               input_tokens=2_000,
                               output_tokens=500,
                               images_per_request=1,
                               audio_seconds_per_request=0)

    # Scenario 2: Medium multimodal app
    print_subheader("Scenario 2: Medium Multimodal App")
    compare_monthly_projection(models,
                               requests_per_day=10_000,
                               input_tokens=2_000,
                               output_tokens=500,
                               images_per_request=1,
                               audio_seconds_per_request=0)

    # Scenario 3: Heavy multimodal app with audio
    print_subheader("Scenario 3: Heavy Multimodal App (with audio)")
    compare_monthly_projection(models,
                               requests_per_day=10_000,
                               input_tokens=5_000,
                               output_tokens=1_000,
                               images_per_request=2,
                               audio_seconds_per_request=30)

    # Scenario 4: Enterprise scale
    print_subheader("Scenario 4: Enterprise Scale")
    compare_monthly_projection(models,
                               requests_per_day=100_000,
                               input_tokens=3_000,
                               output_tokens=1_000,
                               images_per_request=1,
                               audio_seconds_per_request=0)

    # --- Summary ---
    print_header("SUMMARY")
    print()
    print("  GPT-4o:")
    print("    - Best for: Real-time voice, general multimodal, balanced pricing")
    print("    - Audio: Native real-time processing ($100/1M input, $200/1M output)")
    print("    - Weakness: Audio API is expensive at scale")
    print()
    print("  Gemini 2.5 Pro:")
    print("    - Best for: Large context workloads, cost-sensitive multimodal")
    print("    - Audio: Cheapest audio processing ($0.50/1M input)")
    print("    - Weakness: Less real-time voice capability than GPT-4o")
    print()
    print("  Claude Opus 4.1:")
    print("    - Best for: Complex reasoning, highest quality output")
    print("    - Audio: No native audio API")
    print("    - Weakness: 6-7x more expensive than competitors")
    print()
    print("=" * 70)
    print("  Pricing source: Official API docs (mid-2025). Subject to change.")
    print("  Always verify at: openai.com/api/pricing, ai.google.dev/pricing,")
    print("  anthropic.com/pricing")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
