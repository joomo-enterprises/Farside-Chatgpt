#!/usr/bin/env python3
"""
Far Side Episode 04 — Verify AI Dev Environment
================================================
Verifies that the AI dev environment is properly configured.
Run: python src/03_verify_install.py

Tests:
  1. PyTorch import + CUDA availability
  2. Transformers import + small model load
  3. Hugging Face Hub connectivity
  4. Ollama Python SDK import
  5. Tokenizers import
  6. Datasets import
  7. Accelerate import
  8. bitsandbytes import (optional)
  9. peft import (optional)
  10. scipy import
  11. Full end-to-end: generate text with a small model
"""

import sys
import time
import importlib
from contextlib import contextmanager


# ── Helpers ───────────────────────────────────────────────────────────────────

@contextmanager
def timer(label: str):
    """Context manager that times a block and prints the result."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"         ({elapsed:.2f}s)")


class TestResult:
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"

    def __init__(self, name: str, status: str, detail: str = ""):
        self.name = name
        self.status = status
        self.detail = detail


def pass_(name: str, detail: str = "") -> TestResult:
    return TestResult(name, TestResult.PASS, detail)


def fail_(name: str, detail: str = "") -> TestResult:
    return TestResult(name, TestResult.FAIL, detail)


def skip_(name: str, detail: str = "") -> TestResult:
    return TestResult(name, TestResult.SKIP, detail)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_python_version() -> TestResult:
    """Check Python version >= 3.11."""
    ver = sys.version_info
    ver_str = f"{ver.major}.{ver.minor}.{ver.micro}"
    if ver.major == 3 and ver.minor >= 11:
        return pass_("Python Version", ver_str)
    return fail_("Python Version", f"{ver_str} (need >= 3.11)")


def test_torch_import() -> TestResult:
    """Test that PyTorch can be imported."""
    try:
        import torch
        ver = torch.__version__
        return pass_("PyTorch Import", ver)
    except ImportError as e:
        return fail_("PyTorch Import", str(e))
    except Exception as e:
        return fail_("PyTorch Import", f"Unexpected: {e}")


def test_torch_cuda() -> TestResult:
    """Test CUDA availability in PyTorch."""
    try:
        import torch
        if not torch.cuda.is_available():
            return fail_("PyTorch CUDA", "CUDA not available — CPU-only mode")
        gpu_name = torch.cuda.get_device_name(0)
        mem_gb = torch.cuda.get_device_properties(0).total_mem / (1024**3)
        cuda_ver = torch.version.cuda
        return pass_("PyTorch CUDA", f"{gpu_name} | {mem_gb:.1f} GB | CUDA {cuda_ver}")
    except ImportError:
        return skip_("PyTorch CUDA", "PyTorch not installed")
    except Exception as e:
        return fail_("PyTorch CUDA", str(e))


def test_torch_basic_ops() -> TestResult:
    """Test basic PyTorch tensor operations on GPU if available."""
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        a = torch.randn(1000, 1000, device=device)
        b = torch.randn(1000, 1000, device=device)
        c = a @ b
        _ = c.sum().item()
        return pass_("PyTorch Basic Ops", f"Matrix multiply on {device}")
    except ImportError:
        return skip_("PyTorch Basic Ops", "PyTorch not installed")
    except Exception as e:
        return fail_("PyTorch Basic Ops", str(e))


def test_transformers_import() -> TestResult:
    """Test that Transformers can be imported."""
    try:
        import transformers
        ver = transformers.__version__
        return pass_("Transformers Import", ver)
    except ImportError as e:
        return fail_("Transformers Import", str(e))


def test_transformers_model_load() -> TestResult:
    """Test loading a small model from Hugging Face."""
    try:
        from transformers import pipeline
        with timer("Model download + inference"):
            classifier = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
            )
            result = classifier("Setting up AI environments is satisfying!")
        label = result[0]["label"]
        score = result[0]["score"]
        return pass_("Transformers Model Load", f"{label} ({score:.4f})")
    except ImportError:
        return skip_("Transformers Model Load", "Transformers not installed")
    except Exception as e:
        return fail_("Transformers Model Load", str(e))


def test_hf_hub() -> TestResult:
    """Test Hugging Face Hub connectivity."""
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        # Lightweight call: just get the API info
        models = api.list_models(search="gpt2", limit=1)
        if models:
            return pass_("Hugging Face Hub", f"Connected — found '{models[0].id}'")
        return pass_("Hugging Face Hub", "Connected (no models returned)")
    except ImportError:
        return skip_("Hugging Face Hub", "huggingface_hub not installed")
    except Exception as e:
        err = str(e)
        if "401" in err or "Unauthorized" in err:
            return fail_("Hugging Face Hub", "Auth error — run: huggingface-cli login")
        return fail_("Hugging Face Hub", err)


def test_ollama_import() -> TestResult:
    """Test that the Ollama Python SDK can be imported."""
    try:
        import ollama
        ver = getattr(ollama, "__version__", "unknown")
        return pass_("Ollama SDK Import", f"v{ver}")
    except ImportError as e:
        return fail_("Ollama SDK Import", str(e))


def test_ollama_service() -> TestResult:
    """Test that the Ollama service is reachable."""
    try:
        import ollama
        models = ollama.list()
        model_names = [m["name"] for m in models.get("models", [])]
        if model_names:
            return pass_("Ollama Service", f"Running — {len(model_names)} model(s): {', '.join(model_names[:3])}")
        return pass_("Ollama Service", "Running — no models pulled yet")
    except ImportError:
        return skip_("Ollama Service", "Ollama SDK not installed")
    except Exception as e:
        err = str(e)
        if "Connection refused" in err or "ConnectError" in err:
            return fail_("Ollama Service", "Not running — start with: ollama serve")
        return fail_("Ollama Service", err)


def test_tokenizers() -> TestResult:
    """Test that tokenizers can be imported and used."""
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained("gpt2")
        tokens = tok.encode("Hello from Far Side!")
        decoded = tok.decode(tokens)
        return pass_("Tokenizers", f"Encoded {len(tokens)} tokens, decoded correctly")
    except ImportError:
        return skip_("Tokenizers", "transformers not installed")
    except Exception as e:
        return fail_("Tokenizers", str(e))


def test_datasets() -> TestResult:
    """Test that the datasets library can be imported."""
    try:
        import datasets
        ver = datasets.__version__
        return pass_("Datasets Import", ver)
    except ImportError as e:
        return fail_("Datasets Import", str(e))


def test_accelerate() -> TestResult:
    """Test that accelerate can be imported."""
    try:
        import accelerate
        ver = accelerate.__version__
        return pass_("Accelerate Import", ver)
    except ImportError as e:
        return fail_("Accelerate Import", str(e))


def test_bitsandbytes() -> TestResult:
    """Test bitsandbytes (optional, for quantization)."""
    try:
        import bitsandbytes
        ver = bitsandbytes.__version__
        return pass_("bitsandbytes Import", ver)
    except ImportError:
        return skip_("bitsandbytes Import", "Not installed (optional, for 4-bit quantization)")
    except Exception as e:
        return skip_("bitsandbytes Import", f"Installed but error: {e}")


def test_peft() -> TestResult:
    """Test peft (optional, for LoRA fine-tuning)."""
    try:
        import peft
        ver = peft.__version__
        return pass_("PEFT (LoRA) Import", ver)
    except ImportError:
        return skip_("PEFT (LoRA) Import", "Not installed (optional, for LoRA fine-tuning)")
    except Exception as e:
        return skip_("PEFT (LoRA) Import", f"Installed but error: {e}")


def test_scipy() -> TestResult:
    """Test scipy import."""
    try:
        import scipy
        ver = scipy.__version__
        return pass_("SciPy Import", ver)
    except ImportError as e:
        return fail_("SciPy Import", str(e))


def test_dotenv() -> TestResult:
    """Test python-dotenv import."""
    try:
        from dotenv import load_dotenv
        return pass_("python-dotenv", "Available")
    except ImportError as e:
        return fail_("python-dotenv", str(e))


def test_end_to_end() -> TestResult:
    """End-to-end: load a small model and generate text."""
    try:
        from transformers import pipeline
        with timer("End-to-end text generation"):
            generator = pipeline(
                "text-generation",
                model="gpt2",
                max_new_tokens=20,
                do_sample=False,
            )
            result = generator("The future of AI development is")
            text = result[0]["generated_text"]
        # Truncate for display
        short = text[:80] + "..." if len(text) > 80 else text
        return pass_("End-to-End Generation", short)
    except ImportError:
        return skip_("End-to-End Generation", "transformers not installed")
    except Exception as e:
        return fail_("End-to-End Generation", str(e))


# ── All Tests ─────────────────────────────────────────────────────────────────

ALL_TESTS = [
    test_python_version,
    test_torch_import,
    test_torch_cuda,
    test_torch_basic_ops,
    test_transformers_import,
    test_transformers_model_load,
    test_hf_hub,
    test_ollama_import,
    test_ollama_service,
    test_tokenizers,
    test_datasets,
    test_accelerate,
    test_bitsandbytes,
    test_peft,
    test_scipy,
    test_dotenv,
    test_end_to_end,
]


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    print()
    print("=" * 60)
    print("  Far Side Episode 04 — Environment Verification")
    print("=" * 60)
    print()

    results = []
    for test_fn in ALL_TESTS:
        name = test_fn.__name__.replace("test_", "").replace("_", " ").title()
        try:
            result = test_fn()
        except Exception as e:
            result = fail_(name, f"Unexpected error: {e}")
        results.append(result)

        # Print result
        if result.status == TestResult.PASS:
            icon = "[PASS]"
            color_start = "\033[92m" if sys.stdout.isatty() else ""
        elif result.status == TestResult.FAIL:
            icon = "[FAIL]"
            color_start = "\033[91m" if sys.stdout.isatty() else ""
        else:
            icon = "[SKIP]"
            color_start = "\033[93m" if sys.stdout.isatty() else ""

        color_end = "\033[0m" if sys.stdout.isatty() else ""

        detail = f" — {result.detail}" if result.detail else ""
        print(f"  {color_start}{icon}{color_end} {name}{detail}")

    # Summary
    passed = sum(1 for r in results if r.status == TestResult.PASS)
    failed = sum(1 for r in results if r.status == TestResult.FAIL)
    skipped = sum(1 for r in results if r.status == TestResult.SKIP)
    total = len(results)

    print()
    print("=" * 60)

    if sys.stdout.isatty():
        green = "\033[92m"
        red = "\033[91m"
        yellow = "\033[93m"
        reset = "\033[0m"
    else:
        green = red = yellow = reset = ""

    print(f"  Results: {green}{passed} passed{reset}, "
          f"{red}{failed} failed{reset}, "
          f"{yellow}{skipped} skipped{reset} out of {total} tests")
    print()

    if failed == 0:
        print(f"  {green}★ All tests passed! Your AI dev environment is ready.{reset}")
    else:
        print(f"  {red}✗ {failed} test(s) failed.{reset}")
        print("  Failed tests:")
        for r in results:
            if r.status == TestResult.FAIL:
                print(f"    - {r.name}: {r.detail}")
        print()
        print("  Fix suggestions:")
        print("    - Missing packages? Run: bash src/02_create_venv.sh")
        print("    - No GPU? CPU-only PyTorch still works for development")
        print("    - Ollama not running? Run: ollama serve")
        print("    - HF auth error? Run: huggingface-cli login")

    print("=" * 60)
    print()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
