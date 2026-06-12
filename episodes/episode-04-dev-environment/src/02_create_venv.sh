#!/usr/bin/env bash
# ============================================================================
# Far Side Episode 04 — Create AI Dev Environment
# ============================================================================
# Creates a Python virtual environment and installs essential AI packages.
# Usage:   bash src/02_create_venv.sh [venv_dir]
# Default: .venv in the current directory
#
# Requirements: Python 3.11+, pip, internet connection
# ============================================================================

set -euo pipefail

# ── Colors (disable if not a tty) ────────────────────────────────────────────
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' BOLD='' RESET=''
fi

ok()   { echo -e "${GREEN}[OK]${RESET}   $*"; }
warn() { echo -e "${YELLOW}[WARN]${RESET} $*"; }
fail() { echo -e "${RED}[FAIL]${RESET} $*"; }
info() { echo -e "${BLUE}[INFO]${RESET} $*"; }
step() { echo -e "\n${BOLD}── $* ${RESET}"; }

# ── Error handler ─────────────────────────────────────────────────────────────
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        echo
        fail "Setup failed with exit code $exit_code"
        warn "Check the output above for the error."
        warn "Common issues:"
        warn "  - Wrong Python version (need >= 3.11)"
        warn "  - No internet connection"
        warn "  - pip permission errors (never use sudo with venv)"
        warn "  - Compilation errors (install build-essential)"
    fi
}
trap cleanup EXIT

# ── Configuration ─────────────────────────────────────────────────────────────
VENV_DIR="${1:-.venv}"
PYTHON_CMD="python3"

# Packages
CORE_PACKAGES=(
    "pip>=24.0"
    "setuptools>=69.0"
    "wheel>=0.42"
)

AI_PACKAGES=(
    "torch>=2.0"
    "torchvision"
    "torchaudio"
    "transformers>=4.36"
    "datasets>=2.16"
    "tokenizers>=0.15"
    "huggingface_hub>=0.20"
    "accelerate>=0.25"
)

UTIL_PACKAGES=(
    "ollama>=0.4"
    "python-dotenv>=1.0"
    "scipy>=1.11"
    "notebook>=7.0"
    "ipywidgets>=8.0"
    "tqdm>=4.66"
    "rich>=13.0"
)

DEV_PACKAGES=(
    "ruff>=0.1"
    "black>=23.12"
    "pre-commit>=3.6"
    "pytest>=7.4"
)

QUANT_PACKAGES=(
    "bitsandbytes>=0.41"
    "peft>=0.9"
)

# ── Preflight ─────────────────────────────────────────────────────────────────
echo
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║  Far Side Episode 04 — AI Dev Environment Setup        ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${RESET}"
echo

step "Preflight Checks"

# Check Python version
if ! command -v "$PYTHON_CMD" &>/dev/null; then
    fail "python3 not found. Install Python 3.11+ first."
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS:         brew install python@3.11"
    exit 1
fi

PY_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
info "Python version: $PY_VERSION"

PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [[ "$PY_MAJOR" -lt 3 ]] || [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 11 ]]; then
    fail "Need Python >= 3.11, found $PY_VERSION"
    exit 1
fi
ok "Python version requirement met (3.$PY_MINOR)"

# Check internet connectivity
if curl -s --connect-timeout 5 https://pypi.org >/dev/null 2>&1; then
    ok "Internet: reachable"
else
    warn "Internet: cannot reach PyPI — offline install not supported"
    warn "Will attempt to continue with cached packages..."
fi

# Check if venv module is available
if $PYTHON_CMD -c "import venv" 2>/dev/null; then
    ok "venv module: available"
else
    fail "venv module not found. Install python3-venv:"
    echo "  Ubuntu/Debian: sudo apt install python3-venv"
    echo "  Fedora:        sudo dnf install python3-virtualenv"
    exit 1
fi

# Check for existing venv
if [[ -d "$VENV_DIR" ]]; then
    warn "Virtual environment '$VENV_DIR' already exists."
    read -rp "  Delete and recreate? [y/N] " answer
    if [[ "${answer,,}" == "y" || "${answer,,}" == "yes" ]]; then
        info "Removing existing venv..."
        rm -rf "$VENV_DIR"
    else
        info "Keeping existing venv. Installing/upgrading packages into it."
    fi
fi

# ── Create Virtual Environment ────────────────────────────────────────────────
if [[ ! -d "$VENV_DIR" ]]; then
    step "Creating Virtual Environment: $VENV_DIR"

    if $PYTHON_CMD -m venv "$VENV_DIR" --prompt "far-side-ai"; then
        ok "Virtual environment created: $VENV_DIR"
    else
        warn "Standard venv creation failed, trying without --prompt..."
        if ! $PYTHON_CMD -m venv "$VENV_DIR"; then
            fail "Failed to create virtual environment."
            exit 1
        fi
        ok "Virtual environment created (without prompt): $VENV_DIR"
    fi
fi

# Activate
info "Activating virtual environment..."
# Check if we can activate (works in bash/zsh)
VENV_BIN="$VENV_DIR/bin"
if [[ ! -f "$VENV_BIN/activate" ]]; then
    # Windows created the venv — point to Scripts instead
    VENV_BIN="$VENV_DIR/Scripts"
fi

# shellcheck source=/dev/null
source "$VENV_BIN/activate"

ok "Activated: $(which python) -> $(python --version 2>&1)"

# ── Upgrade pip ───────────────────────────────────────────────────────────────
step "Upgrading pip, setuptools, wheel"
pip install --upgrade "${CORE_PACKAGES[@]}" 2>&1 | tail -3
ok "Core tools upgraded"

# ── Install AI Packages ───────────────────────────────────────────────────────
step "Installing AI/ML packages (this may take a while...)"
info "PyTorch + Transformers + Hugging Face tools..."
echo

# Try to detect CUDA and install appropriate torch
if command -v nvidia-smi &>/dev/null; then
    CUDA_VER=$(nvidia-smi | grep "CUDA Version" | sed 's/.*Version //' | sed 's/ .*//' | cut -d. -f1,2)
    info "NVIDIA GPU detected, CUDA $CUDA_VER"

    # Map CUDA version to PyTorch index
    CUDA_MAJOR=$(echo "$CUDA_VER" | cut -d. -f1)
    CUDA_MINOR=$(echo "$CUDA_VER" | cut -d. -f2)

    if [[ "$CUDA_MAJOR" -ge 12 && "$CUDA_MINOR" -ge 4 ]]; then
        TORCH_INDEX="https://download.pytorch.org/whl/cu124"
    elif [[ "$CUDA_MAJOR" -ge 12 && "$CUDA_MINOR" -ge 1 ]]; then
        TORCH_INDEX="https://download.pytorch.org/whl/cu121"
    elif [[ "$CUDA_MAJOR" -ge 11 && "$CUDA_MINOR" -ge 8 ]]; then
        TORCH_INDEX="https://download.pytorch.org/whl/cu118"
    else
        TORCH_INDEX="https://download.pytorch.org/whl/cpu"
        warn "CUDA $CUDA_VER not well supported — installing CPU-only PyTorch"
    fi

    info "Installing PyTorch from: $TORCH_INDEX"
    pip install torch torchvision torchaudio \
        --index-url "$TORCH_INDEX" 2>&1 | tail -5
    ok "PyTorch installed (CUDA enabled)"
else
    warn "No NVIDIA GPU detected — installing CPU-only PyTorch"
    warn "For GPU support, install NVIDIA drivers and CUDA toolkit first"
    pip install torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/cpu 2>&1 | tail -5
    ok "PyTorch installed (CPU only)"
fi

echo
info "Installing Transformers, Datasets, Hugging Face Hub..."
pip install "${AI_PACKAGES[@]}" 2>&1 | tail -5
ok "AI packages installed"

# ── Install Utility Packages ──────────────────────────────────────────────────
step "Installing Utility Packages"
pip install "${UTIL_PACKAGES[@]}" 2>&1 | tail -5
ok "Utility packages installed"

# ── Install Dev Packages ──────────────────────────────────────────────────────
step "Installing Development Tools"
pip install "${DEV_PACKAGES[@]}" 2>&1 | tail -5
ok "Dev tools installed"

# ── Install Quantization Packages ─────────────────────────────────────────────
step "Installing Quantization Packages (bitsandbytes, peft)"
if pip install "${QUANT_PACKAGES[@]}" 2>&1 | tail -5; then
    ok "Quantization packages installed"
else
    warn "Quantization packages failed to install (non-critical)"
    warn "bitsandbytes requires CUDA — skip if using CPU-only"
fi

# ── Generate requirements.txt ─────────────────────────────────────────────────
step "Generating requirements.txt"
pip freeze > requirements.txt
ok "requirements.txt created ($(wc -l < requirements.txt) packages)"

# ── Create .env template ─────────────────────────────────────────────────────
step "Creating .env template"
if [[ ! -f .env ]]; then
    cat > .env << 'ENVEOF'
# Far Side Episode 04 — Environment Variables
# Copy this to .env and fill in your keys (never commit .env!)

# Hugging Face (get from huggingface.co/settings/tokens)
HF_TOKEN=

# OpenAI (get from platform.openai.com/api-keys)
OPENAI_API_KEY=

# OpenRouter — OpenAI-compatible, many models (openrouter.ai/keys)
OPENROUTER_API_KEY=

# Anthropic (console.anthropic.com)
ANTHROPIC_API_KEY=

# Weights & Biases (wandb.ai/authorize)
WANDB_API_KEY=
ENVEOF
    chmod 600 .env
    ok ".env template created (chmod 600)"
else
    warn ".env already exists — skipping template creation"
fi

# ── Create .gitignore ─────────────────────────────────────────────────────────
step "Creating .gitignore"
if [[ ! -f .gitignore ]]; then
    cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
*.egg

# Virtual Environment
.venv/
venv/
ENV/

# Environment Variables — NEVER COMMIT
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Jupyter
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db

# Data (large files)
data/raw/
data/processed/
*.parquet
*.h5
*.hdf5

# Model checkpoints (large — use Git LFS or DVC for these)
models/
checkpoints/
*.pt
*.pth
*.bin
*.safetensors
*.gguf
GITIGNORE
    ok ".gitignore created"
else
    warn ".gitignore already exists — skipping"
fi

# ── Create project structure ──────────────────────────────────────────────────
step "Creating Project Structure"
mkdir -p src tests notebooks data/raw data/processed configs
ok "Project directories created:"
info "  src/          — Source code"
info "  tests/        — Test files"
info "  notebooks/    — Jupyter notebooks"
info "  data/raw/     — Raw datasets"
info "  data/processed/— Processed data"
info "  configs/      — Configuration files"

# ── Summary ───────────────────────────────────────────────────────────────────
echo
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║  Setup Complete!                                        ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${RESET}"
echo
ok "Virtual environment: $VENV_DIR"
ok "Python:             $(python --version 2>&1)"
ok "pip:                $(pip --version 2>&1 | awk '{print $1, $2}')"
ok "Packages installed: $(pip list --format=columns 2>/dev/null | tail -n +3 | wc -l)"
echo
info "Next steps:"
echo "  1. Activate:     source $VENV_BIN/activate"
echo "  2. Verify:       python src/03_verify_install.py"
echo "  3. Set up keys:  cp .env.example .env  # then edit with your keys"
echo "  4. Start coding: python src/01_setup_check.py"
echo
info "To deactivate when done: deactivate"
echo
