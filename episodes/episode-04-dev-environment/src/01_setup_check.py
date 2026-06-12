#!/usr/bin/env python3
"""
Far Side Episode 04 — System Setup Checker
==========================================
Checks if all required tools for the AI dev environment are installed.
Run: python3 src/01_setup_check.py

Returns exit code 0 if all critical checks pass, 1 if any fail.
"""

import shutil
import subprocess
import sys
import os
import importlib.util
from dataclasses import dataclass, field
from typing import Optional


# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a shell command, capture output."""
    return subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout
    )


# ── Check Functions ──────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""
    critical: bool = True
    section: str = "general"


def check_python() -> CheckResult:
    """Check Python version >= 3.11"""
    r = run("python3 --version")
    if r.returncode != 0:
        return CheckResult("Python 3", False, "python3 not found", True, "core")
    ver = r.stdout.strip()
    parts = ver.split()[1].split(".")
    major, minor = int(parts[0]), int(parts[1])
    if major == 3 and minor >= 11:
        return CheckResult("Python 3", True, ver, True, "core")
    return CheckResult(
        "Python 3", False, f"{ver} (need >= 3.11)", True, "core"
    )


def check_pip() -> CheckResult:
    """Check pip is available and up-to-date."""
    r = run("pip --version")
    if r.returncode != 0:
        r = run("pip3 --version")
    if r.returncode != 0:
        return CheckResult("pip", False, "pip not found", True, "core")
    return CheckResult("pip", True, r.stdout.strip(), True, "core")


def check_git() -> CheckResult:
    """Check git is installed."""
    r = run("git --version")
    if r.returncode != 0:
        return CheckResult("Git", False, "git not found", True, "core")
    return CheckResult("Git", True, r.stdout.strip(), True, "core")


def check_venv() -> CheckResult:
    """Check python3-venv module is importable."""
    spec = importlib.util.find_spec("venv")
    if spec:
        return CheckResult("venv module", True, "Available", True, "core")
    return CheckResult(
        "venv module", False, "python3-venv package may be missing", True, "core"
    )


def check_nvidia_smi() -> CheckResult:
    """Check nvidia-smi is available."""
    path = shutil.which("nvidia-smi")
    if path is None:
        return CheckResult(
            "nvidia-smi", False,
            "Not found — GPU tools won't work without NVIDIA drivers",
            False, "gpu"
        )
    r = run("nvidia-smi --query-gpu=name,memory.total,driver_version "
            "--format=csv,noheader")
    if r.returncode != 0:
        return CheckResult("nvidia-smi", Present=True, detail="Found but failed to query GPU", section="gpu")
    gpu_info = r.stdout.strip()
    return CheckResult("nvidia-smi", True, gpu_info, False, "gpu")


def check_cuda() -> CheckResult:
    """Check CUDA toolkit via nvcc."""
    path = shutil.which("nvcc")
    if path is None:
        return CheckResult(
            "nvcc (CUDA Toolkit)", False,
            "Not found — install CUDA toolkit for GPU compute",
            False, "gpu"
        )
    r = run("nvcc --version | grep release")
    detail = r.stdout.strip().split("\n")[0] if r.stdout.strip() else "nvcc available"
    return CheckResult("nvcc (CUDA Toolkit)", True, detail, False, "gpu")


def check_docker() -> CheckResult:
    """Check Docker is installed."""
    r = run("docker --version")
    if r.returncode != 0:
        return CheckResult("Docker", False, "Not found (optional, for vLLM)", False, "devops")
    return CheckResult("Docker", True, r.stdout.strip(), False, "devops")


def check_ollama() -> CheckResult:
    """Check Ollama is installed."""
    path = shutil.which("ollama")
    if path is None:
        return CheckResult(
            "Ollama", False,
            "Not found — curl -fsSL https://ollama.com/install.sh | sh",
            False, "local-models"
        )
    r = run("ollama --version")
    detail = r.stdout.strip() if r.returncode == 0 else "Found but version check failed"
    return CheckResult("Ollama", True, detail, False, "local-models")


def check_ollama_service() -> CheckResult:
    """Check if Ollama service is running."""
    r = run("curl -s http://localhost:11434/api/tags -o /dev/null -w '%{http_code}'")
    if r.stdout.strip() == "200":
        return CheckResult("Ollama Service", True, "Running on port 11434", False, "local-models")
    return CheckResult(
        "Ollama Service", False,
        "Not running — start with: ollama serve",
        False, "local-models"
    )


def check_hf_cli() -> CheckResult:
    """Check Hugging Face CLI."""
    path = shutil.which("huggingface-cli")
    if path is None:
        return CheckResult(
            "huggingface-cli", False,
            "Not found — install with: pip install -U 'huggingface_hub[cli]'",
            False, "hf"
        )
    r = run("huggingface-cli --version")
    detail = r.stdout.strip() if r.returncode == 0 else "Found"
    return CheckResult("huggingface-cli", True, detail, False, "hf")


def check_cursor() -> CheckResult:
    """Check Cursor IDE."""
    path = shutil.which("cursor")
    if path is None:
        return CheckResult("Cursor IDE", False, "Not found (optional)", False, "ide")
    return CheckResult("Cursor IDE", True, f"Found at {path}", False, "ide")


def check_vscode() -> CheckResult:
    """Check VS Code."""
    path = shutil.which("code")
    if path is None:
        return CheckResult("VS Code", False, "Not found (optional)", False, "ide")
    return CheckResult("VS Code", True, f"Found at {path}", False, "ide")


def check_disk_space() -> CheckResult:
    """Check available disk space."""
    st = os.statvfs(os.path.expanduser("~"))
    free_gb = (st.f_bavail * st.f_frsize) / (1024 ** 3)
    if free_gb >= 50:
        return CheckResult("Disk Space", True, f"{free_gb:.1f} GB free", True, "system")
    return CheckResult(
        "Disk Space", False,
        f"{free_gb:.1f} GB free — AI models need significant space",
        True, "system"
    )


def check_ram() -> CheckResult:
    """Check available RAM."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    gb = kb / (1024 ** 2)
                    return CheckResult(
                        "System RAM", True, f"{gb:.1f} GB total", True, "system"
                    )
    except (FileNotFoundError, ValueError):
        pass
    # macOS fallback
    r = run("sysctl -n hw.memsize")
    if r.returncode == 0:
        gb = int(r.stdout.strip()) / (1024**3)
        return CheckResult("System RAM", True, f"{gb:.1f} GB total", True, "system")
    return CheckResult("System RAM", False, "Unable to detect", True, "system")


# ── Sections ─────────────────────────────────────────────────────────────────

SECTIONS = [
    ("core", "Core Tools (Python, pip, Git, venv)"),
    ("gpu", "GPU & CUDA"),
    ("local-models", "Local Models (Ollama)"),
    ("hf", "Hugging Face"),
    ("devops", "DevOps (Docker)"),
    ("ide", "Development Environment (Cursor, VS Code)"),
    ("system", "System Resources (Disk, RAM)"),
]

ALL_CHECKS = [
    check_python,
    check_pip,
    check_git,
    check_venv,
    check_nvidia_smi,
    check_cuda,
    check_ollama,
    check_ollama_service,
    check_hf_cli,
    check_docker,
    check_cursor,
    check_vscode,
    check_disk_space,
    check_ram,
]


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    print()
    print("=" * 60)
    print("  Far Side Episode 04 — AI Dev Environment Setup Check")
    print("=" * 60)
    print()

    results = [fn() for fn in ALL_CHECKS]

    critical_pass = 0
    critical_fail = 0
    optional_pass = 0
    optional_fail = 0

    for section_id, section_name in SECTIONS:
        section_results = [r for r in results if r.section == section_id]
        if not section_results:
            continue

        print(f"  {section_name}")
        print(f"  {'─' * (len(section_name) + 2)}")

        for r in section_results:
            icon = "[PASS]" if r.ok else "[FAIL]"
            crit = " *" if r.critical else ""
            detail = f" — {r.detail}" if r.detail else ""

            # Color: green for pass, red for fail
            if sys.stdout.isatty():
                color = "\033[92m" if r.ok else "\033[91m"
                reset = "\033[0m"
            else:
                color = reset = ""

            print(f"    {color}{icon}{reset} {r.name}{crit}{detail}")

            if r.critical:
                if r.ok:
                    critical_pass += 1
                else:
                    critical_fail += 1
            else:
                if r.ok:
                    optional_pass += 1
                else:
                    optional_fail += 1

        print()

    # Summary
    total_pass = critical_pass + optional_pass
    total_fail = critical_fail + optional_fail
    total = total_pass + total_fail

    print("=" * 60)
    if sys.stdout.isatty():
        green = "\033[92m"
        red = "\033[91m"
        reset = "\033[0m"
    else:
        green = red = reset = ""

    print(f"  Results: {green}{total_pass} passed{reset}, "
          f"{red}{total_fail} failed{reset} out of {total} checks")
    print(f"  Critical: {green}{critical_pass} passed{reset}, "
          f"{red}{critical_fail} failed{reset}")
    print(f"  Optional: {green}{optional_pass} passed{reset}, "
          f"{red}{optional_fail} failed{reset}")
    print()

    if critical_fail == 0:
        print(f"  {green}★ All critical checks passed! You're ready to build.{reset}")
    else:
        print(f"  {red}✗ {critical_fail} critical check(s) failed. "
              f"Fix those first — see the script for install hints.{reset}")
        print("    Critical items are marked with * in the output above.")
    print("=" * 60)
    print()

    return 0 if critical_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
