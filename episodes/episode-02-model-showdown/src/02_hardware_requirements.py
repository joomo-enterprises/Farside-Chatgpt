#!/usr/bin/env python3
"""
Episode 02 — Hardware Requirements Calculator
On The FarSide Series | FarSide ChatGPT by NinjaTech AI Team

Calculates VRAM and RAM requirements for running open-source LLMs at
different precision levels (FP16, 8-bit, 4-bit) across model sizes
(7B, 13B, 70B parameters).

Usage:
    python src/02_hardware_requirements.py
"""

import sys
import math

# Model sizes and their parameter counts
MODEL_SIZES = {
    "7B":   {"params": 7_000_000_000,   "examples": "Llama 3.2 7B, Mistral 7B, Gemma 3 9B (~7B)"},
    "13B":  {"params": 13_000_000_000,  "examples": "Llama 3.2 13B, Codestral 22B (~13B active)"},
    "70B":  {"params": 70_000_000_000,  "examples": "Llama 4 Scout 109B/17B active (~70B), Mistral Large"},
}

# Quantization levels and their bytes per parameter
QUANTIZATION = {
    "FP16":   {"bits": 16, "bytes_per_param": 2.0, "quality": "Highest (lossless)"},
    "8-bit":  {"bits": 8,  "bytes_per_param": 1.0, "quality": "Excellent (~lossless)"},
    "Q4_K_M": {"bits": 4,  "bytes_per_param": 0.5, "quality": "Very Good (minimal loss)"},
    "Q3_K_M": {"bits": 3,  "bytes_per_param": 0.375, "quality": "Good (noticeable on complex tasks)"},
    "Q2_K":   {"bits": 2,  "bytes_per_param": 0.25, "quality": "Acceptable (quality drop visible)"},
}

# Overhead percentages for KV cache and operating system
KV_CACHE_OVERHEAD = 1.20  # 20% extra for context/attention cache
OS_OVERHEAD_GB = 1.5      # Base system + framework overhead

# Popular consumer GPUs for reference
REFERENCE_GPUS = [
    ("Intel UHD (integrated)", 0),     # Uses system RAM
    ("RTX 3060 12GB", 12),
    ("RTX 3070 8GB", 8),
    ("RTX 4060 Ti 16GB", 16),
    ("RTX 3080 10GB", 10),
    ("RTX 3090 24GB", 24),
    ("RTX 4070 Ti 16GB", 16),
    ("RTX 4080 16GB", 16),
    ("RTX 4090 24GB", 24),
    ("RTX 6000 Ada 48GB", 48),
    ("A100 40GB", 40),
    ("A100 80GB", 80),
    ("H100 80GB", 80),
]


# ─── Formatting Helpers ──────────────────────────────────────────────────────

def format_size(gb):
    """Format gigabyte values nicely."""
    if gb >= 1024:
        return f"{gb / 1024:.1f} TB"
    elif gb >= 1:
        return f"{gb:.1f} GB"
    else:
        return f"{gb * 1024:.0f} MB"


def fit_indicator(required_gb, vram_gb):
    """Return a visual indicator showing if a GPU can handle the model."""
    if vram_gb == 0:
        return "  (CPU only)"
    ratio = required_gb / vram_gb
    if ratio <= 0.7:
        return "  ✅ Fits easily"
    elif ratio <= 0.9:
        return "  ⚠️  Tight fit"
    elif ratio <= 1.0:
        return "  🔴 Barely fits"
    else:
        return f"  ❌ Needs {required_gb - vram_gb:.1f} GB more"


def print_separator(char="═", width=100):
    print(char * width)


# ─── Main Output ─────────────────────────────────────────────────────────────

def print_header():
    print()
    print_separator("╔" + "═" * 98 + "╗")
    print("║" + "  ON THE FARSIDE SERIES — Episode 02".center(98) + "║")
    print("║" + "  Hardware Requirements Calculator".center(98) + "║")
    print("║" + "  VRAM / RAM for LLM Inference".center(98) + "║")
    print_separator("╚" + "═" * 98 + "╝")
    print()
    print("  Series: On The FarSide Series")
    print("  Book:   FarSide ChatGPT — NinjaTech AI Team / Joomo Enterprises Publishing")
    print()


def print_formula_explained():
    print_section_header("HOW IT WORKS")
    print()
    print("  Memory required = (Parameters × Bytes per Parameter) × KV_Cache_Overhead + OS_Overhead")
    print()
    print("  Each parameter in the model is stored as a number. The precision of that")
    print("  number determines how much memory it takes:")
    print()
    print("    FP16  (16-bit float)  = 2 bytes per parameter")
    print("    8-bit (8-bit integer) = 1 byte per parameter")
    print("    4-bit (4-bit integer) = 0.5 bytes per parameter  ← most popular for consumers")
    print("    3-bit (3-bit integer) = 0.375 bytes per parameter")
    print("    2-bit (2-bit integer) = 0.25 bytes per parameter")
    print()
    print("  We also add 20% overhead for the attention/KV cache and ~1.5 GB for")
    print("  the framework (llama.cpp, Ollama, etc).")
    print()


def print_requirements_table():
    print_section_header("VRAM / RAM REQUIREMENTS BY MODEL SIZE & PRECISION")
    print()

    # Header
    header = f"  {'Model Size':<13} {'FP16':>10} {'8-bit':>10} {'Q4_K_M':>10} {'Q3_K_M':>10} {'Q2_K':>10}"
    print(header)
    print("  " + "-" * 63)

    for size_name, size_data in MODEL_SIZES.items():
        row = f"  {size_name:<13}"
        for quant_name, quant_data in QUANTIZATION.items():
            raw_bytes = size_data["params"] * quant_data["bytes_per_param"]
            raw_gb = raw_bytes / (1024 ** 3)
            total_gb = raw_gb * KV_CACHE_OVERHEAD + OS_OVERHEAD_GB
            row += f" {format_size(total_gb):>10}"
        print(row)

    print("  " + "-" * 63)
    print()
    print("  Note: Requirements include 20% KV cache overhead + 1.5 GB framework overhead.")
    print()


def print_detailed_breakdown():
    print_section_header("DETAILED BREAKDOWN: 70B MODEL AT DIFFERENT PRECISIONS")
    print()
    print("  The 70B class (e.g., LLaMA 4 Scout) is the most demanding. Here's the")
    print("  exact math for each quantization level:")
    print()

    params = MODEL_SIZES["70B"]["params"]

    for quant_name, quant_data in QUANTIZATION.items():
        raw_bytes = params * quant_data["bytes_per_param"]
        raw_gb = raw_bytes / (1024 ** 3)
        kv_overhead = raw_gb * (KV_CACHE_OVERHEAD - 1.0)
        total_gb = raw_gb * KV_CACHE_OVERHEAD + OS_OVERHEAD_GB

        print(f"  ── {quant_name} ({quant_data['bits']}-bit) ──")
        print(f"     Raw model:      {format_size(raw_gb)} ({raw_bytes:,.0f} bytes)")
        print(f"     KV cache (20%):  +{format_size(kv_overhead)}")
        print(f"     Framework:       +{format_size(OS_OVERHEAD_GB)}")
        print(f"     Total required:  {format_size(total_gb)}")
        print(f"     Quality:         {quant_data['quality']}")
        print()


def print_gpu_recommendations():
    print_section_header("GPU RECOMMENDATIONS BY USE CASE")
    print()

    configurations = [
        ("Budget / Entry Level",
         [("7B", "Q4_K_M"), ("7B", "FP16"), ("13B", "Q2_K")],
         "Laptop, desktop with entry GPU"),

        ("Mid-Range / Sweet Spot",
         [("13B", "Q4_K_M"), ("7B", "FP16"), ("70B", "Q2_K")],
         "RTX 3070/3080/4060Ti/4070 class"),

        ("High-End Enthusiast",
         [("70B", "Q4_K_M"), ("13B", "FP16"), ("70B", "Q3_K_M")],
         "RTX 3090/4090/4080 class"),

        ("Professional / Workstation",
         [("70B", "FP16"), ("70B", "Q4_K_M"), ("70B", "8-bit")],
         "RTX 6000 Ada, A100, H100"),
    ]

    for title, configs, hardware_desc in configurations:
        print(f"  ┌─ {title} ── {hardware_desc}")
        print(f"  │")
        for model_size, quant in configs:
            params = MODEL_SIZES[model_size]["params"]
            bp = QUANTIZATION[quant]["bytes_per_param"]
            raw_gb = (params * bp) / (1024 ** 3)
            total_gb = raw_gb * KV_CACHE_OVERHEAD + OS_OVERHEAD_GB
            print(f"  │  {model_size} @ {quant:<6}  →  {format_size(total_gb):>9}  needed")
        print(f"  │")
        print(f"  └{'─' * 60}")
        print()


def print_popular_gpus():
    print_section_header("REFERENCE: POPULAR GPUs AND WHAT THEY CAN RUN")
    print()

    header = f"  {'GPU':<26} {'VRAM':>6}  {'7B Q4':>8} {'13B Q4':>8} {'70B Q4':>8}"
    print(header)
    print("  " + "-" * 54)

    for gpu_name, vram in REFERENCE_GPUS:
        if vram == 0:
            row = f"  {gpu_name:<26} {'RAM':>6}  {'───':>8} {'───':>8} {'───':>8}"
        else:
            # Calculate what fits
            results = []
            for model_size in ["7B", "13B", "70B"]:
                params = MODEL_SIZES[model_size]["params"]
                for quant in ["Q4_K_M"]:
                    bp = QUANTIZATION[quant]["bytes_per_param"]
                    req_gb = (params * bp) / (1024 ** 3) * KV_CACHE_OVERHEAD + OS_OVERHEAD_GB
                    indicator = "✅" if req_gb <= vram * 0.85 else "❌"
                    results.append(f"{indicator:>8}")
            row = f"  {gpu_name:<26} {vram:>5}G  {results[0]:>8} {results[1]:>8} {results[2]:>8}"
        print(row)

    print()
    print("  ✅ = Comfortable fit (uses <85% of VRAM)")
    print("  ❌ = Won't fit (or needs offloading)")
    print()


def print_mac_studio_note():
    print_section_header("SPECIAL NOTE: APPLE SILICON (UNIFIED MEMORY)")
    print()
    print("  Apple Silicon Macs (M1/M2/M3/M4) use unified memory shared between")
    print("  CPU and GPU. This makes them excellent for running LLMs because the")
    print("  entire model can fit in system RAM without VRAM limitations:")
    print()
    print("    MacBook Air  M2  16GB →  7B Q4 ✅  |  13B Q4 ✅   |  70B ❌")
    print("    MacBook Pro  M3  18GB →  7B Q4 ✅  |  13B Q4 ✅   |  70B ❌")
    print("    MacBook Pro  M4  24GB →  7B Q4 ✅  |  13B Q4 ✅   |  70B Q4 ⚠️")
    print("    Mac Studio    M4  64GB →  7B Q4 ✅  |  13B Q4 ✅   |  70B Q4 ✅")
    print("    Mac Studio    M4  128GB →  70B FP16 ✅  |  Any model fits")
    print()
    print("  Note: ⚠️ = Fits but uses most of available memory (doable but tight)")
    print()


def print_ollama_commands():
    print_section_header("QUICK START WITH OLLAMA")
    print()
    print("  Once you know what fits, here are the commands to get started:")
    print()
    print("    # Install Ollama: https://ollama.com")
    print()
    print("    # Pull and run models")
    print("    ollama run llama3.2          # LLaMA 3.2 8B (default Q4)")
    print("    ollama run mistral          # Mistral 7B")
    print("    ollama run gemma3           # Gemma 3 (specify size: gemma3:9b)")
    print("    ollama run codestral        # Mistral's code-specialized model")
    print()
    print("    # Check what's running")
    print("    ollama list")
    print()
    print("    # Check GPU memory usage (NVIDIA)")
    print("    watch -n1 nvidia-smi")
    print()
    print("    # Check unified memory (macOS)")
    print("    vm_stat | head -10")
    print()


def print_recommendation():
    print_section_header("BOTTOM LINE")
    print()
    print("  ┌─────────────────────────────────────────────────────────────────────────────┐")
    print("  │  'What can I run?' — The simple answer:                                      │")
    print("  │                                                                             │")
    print("  │  8GB VRAM  (RTX 3070/4060)    →  7B models at 4-bit. Perfectly usable.   │")
    print("  │  12GB VRAM (RTX 3060/3080)    →  Up to 13B at 4-bit. Sweet spot.         │")
    print("  │  16GB VRAM (RTX 4070/4080)    →  13B at 4-bit, maybe 70B at 2-bit.       │")
    print("  │  24GB VRAM (RTX 3090/4090)    →  70B at 4-bit. The enthusiast dream.     │")
    print("  │  48GB VRAM (RTX 6000/Ada)     →  70B at 8-bit. Professional grade.       │")
    print("  │  No GPU   (CPU only)          →  7B at 4-bit, slow but functional.       │")
    print("  └─────────────────────────────────────────────────────────────────────────────┘")
    print()


def print_footer():
    print_separator()
    print("  On The FarSide Series — Episode 02")
    print("  Book: FarSide ChatGPT by NinjaTech AI Team")
    print("  Published by Joomo Enterprises Publishing")
    print()
    print("  Estimates are approximate. Actual requirements vary by sequence length,")
    print("  batch size, and inference framework used.")
    print_separator()
    print()


def print_section_header(title):
    print()
    print_separator()
    print(f"  {title}")
    print_separator()


def main():
    print_header()
    print_formula_explained()
    print_requirements_table()
    print_detailed_breakdown()
    print_gpu_recommendations()
    print_popular_gpus()
    print_mac_studio_note()
    print_ollama_commands()
    print_recommendation()
    print_footer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
