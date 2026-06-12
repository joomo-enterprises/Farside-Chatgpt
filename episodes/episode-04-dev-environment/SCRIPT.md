# Episode 4: Setting Up Your AI Dev Environment in 2025 (Python + Open Source)

**Channel:** On The FarSide Series  
**Duration:** ~28 minutes  
**Hook:** "Stop watching tutorials and start building. Here is your complete AI dev setup."

---

## TABLE OF CONTENTS

1. [00:00–01:30 — Cold Open & Hook](#cold-open--hook)
2. [01:30–03:30 — The Philosophy: Why This Setup?](#the-philosophy-why-this-setup)
3. [03:30–07:00 — Python Virtual Environments Done Right](#python-virtual-environments-done-right)
4. [07:00–11:00 — PyTorch + CUDA Install](#torch--cuda-install)
5. [11:00–14:00 — Hugging Face Setup](#hugging-face-setup)
6. [14:00–17:30 — Ollama: Local Models](#ollama-local-models)
7. [17:30–21:00 — vLLM for High-Throughput Serving](#vllm-for-high-throughput-serving)
8. [21:00–24:00 — IDE Setup: Cursor & VS Code](#ide-setup-cursor--vs-code)
9. [24:00–26:00 — API Key Management & Security](#api-key-management--security)
10. [26:00–28:00 — Cost Monitoring & Wrap-Up](#cost-monitoring--wrap-up)

---

## COLD OPEN & HOOK

**[00:00–01:30]**

**[ON SCREEN: Clips of scrolling through endless YouTube tutorials, "Learn AI in 10 Minutes!" thumbnails, someone closing their laptop in frustration]**

**HOST:**

"If you've spent more time watching tutorials than actually building AI projects... you're not alone. The internet is drowning in 'How to Use ChatGPT' and 'AI Explained in 5 Minutes' content. But you? You want to actually *build* things. Fine-tune models. Run inference locally. Deploy your own LLM API without burning cash."

**[ON SCREEN: Hook text appears]**

"Stop watching tutorials and start building. Here is your complete AI dev setup for 2025 — Python, PyTorch, Hugging Face, Ollama, vLLM, proper IDE config, API key management, and cost monitoring. Everything open source. Everything real."

"By the end of this video, you'll have a fully functional AI development environment and the scripts to set it up from scratch on any machine in under 30 minutes."

"Let's get into it."

---

## THE PHILOSOPHY: WHY THIS SETUP?

**[01:30–03:30]**

**HOST:**

"Before we touch a single command, let's talk about *why* this specific stack. There are a million ways to set up an AI environment, but this one is optimized for three things:"

"[1] **Reproducibility** — Every dependency pinned, every environment isolated. No more 'works on my machine' excuses."

"[2] **Cost efficiency** — Local inference with Ollama when you don't need the cloud. Cloud GPUs when you do. No surprise bills."

"[3] **Speed to build** — Cursor for fast prototyping, VS Code for deep work. Virtual environments so your projects don't collide."

"Here's what we're installing today:"

**[ON SCREEN: Appears as a checklist animation]**
- Python 3.11+ with venv
- PyTorch with CUDA 12.4 support
- Hugging Face Hub + Transformers
- Ollama for local model inference
- vLLM for production serving
- Developer tooling (Cursor, VS Code, Git)
- API key management with environment variables
- Cost monitoring with OpenRouter tracking

"No fluff. No detours. Let's set up."

---

## PYTHON VIRTUAL ENVIRONMENTS DONE RIGHT

**[03:30–07:00]**

**HOST:**

"First things first: Python virtual environments. If you're installing packages globally right now, stop. I'm serious. You will create dependency conflicts that haunt you at 2 AM three months from now."

**[LIVE DEMO — Terminal opens]**

```bash
# Check your Python version
python3 --version
# Expected: Python 3.11 or higher

# Check if venv is available (it ships with Python 3.3+)
python3 -c "import venv; print('venv available')"

# Create the project directory
mkdir -p ~/ai-projects/my-llm-app
cd ~/ai-projects/my-llm-app

# Create a virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Verify you're inside it
which python
# Should show: ~/ai-projects/my-llm-app/.venv/bin/python

# Upgrade pip first — always do this
pip install --upgrade pip setuptools wheel

# Check versions
pip --version
python --version
```

**HOST:**

"Notice I'm using `python3 -m venv` — the recommended way. This ensures you're using the Python interpreter you expect. No aliases, no confusion."

"Here's why this matters:"

**[ON SCREEN: Diagram showing system Python vs venv Python]**

"System Python is for your OS. Virtual environments are for your projects. When you activate a venv, your PATH gets rewritten so `python` and `pip` point to the venv. Every package you install stays *inside* that venv. Delete the folder, delete the environment. Clean."

"Let me show you the setup check script that comes with this episode:"

**[LIVE DEMO — Opening src/01_setup_check.py]**

```python
# We'll walk through this later, but here's the idea:
python src/01_setup_check.py
# Gives you a full system report: what's installed, what's missing
```

"Download link is in the description. Let's keep moving."

---

## PYTORCH + CUDA INSTALL

**[07:00–11:00]**

**HOST:**

"Now the big one: PyTorch with GPU support. This is where people get stuck, so I'm going to walk you through it step by step."

"First, check what GPU you have:"

```bash
# NVIDIA GPU check
nvidia-smi
# This shows your GPU model, driver version, CUDA version

# If you don't have this, you need to install NVIDIA drivers first
# On Linux:
sudo apt update && sudo apt install nvidia-driver-550
# (or whatever's latest for your card)
```

**HOST:**

"`nvidia-smi` is your first checkpoint. If this doesn't work, nothing GPU-related will. Fix your drivers *before* trying to install PyTorch."

"[ON SCREEN: nvidia-smi output annotated with callouts]**

"See that top row? That tells you your driver version and the maximum CUDA version your driver supports. Match this to the PyTorch install command."

**[LIVE DEMO — Terminal]**

```bash
# Check your CUDA version from nvidia-smi output
# Look at the top-right corner of the table

# For CUDA 12.4 (recommended for 2025):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# For CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# If you have no GPU — CPU only (still useful for development):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**HOST:**

"The key here is `--index-url`. You're pulling the CUDA-enabled wheel from PyTorch's own package index, not the default PyPI. This is the single most common mistake people make."

"Let's verify it works:"

```bash
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'CUDA version: {torch.version.cuda}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB')
"
```

**HOST:**

"If that prints 'CUDA available: True' and shows your GPU — congratulations, the hard part is done. If it says False, don't panic. Let me show you the three most common fixes:"

**[ON SCREEN: Troubleshooting list]**

```bash
# Fix 1: Wrong PyTorch version for your CUDA
# Check compatibility: your driver supports CUDA X, but you installed CUDA Y
# Solution: reinstall with the correct --index-url

# Fix 2: Missing CUDA runtime libraries
# Solution: Install CUDA toolkit alongside PyTorch
sudo apt install cuda-toolkit-12-4

# Fix 3: Environment variable issue
export LD_LIBRARY_PATH=/usr/local/cuda-12.4/lib64:$LD_LIBRARY_PATH
```

"After PyTorch, we also need cuDNN — it comes bundled with the wheel, but let's confirm:"

```bash
python3 -c "import torch; print(f'cuDNN: {torch.backends.cudnn.version()}')"
```

"If that returns a number, everything is wired up correctly."

---

## HUGGING FACE SETUP

**[11:00–14:00]**

**HOST:**

"Hugging Face is the GitHub of AI models. Transformers, datasets, tokenizers — it's the standard library for modern NLP. Let's set it up."

**[LIVE DEMO]**

```bash
# Install the core packages inside your venv
pip install transformers
pip install datasets
pip install tokenizers
pip install huggingface_hub
pip install accelerate     # For efficient multi-device inference
pip install sentencepiece  # Some models need this tokenizer
pip install protobuf       # Required for some model configs
```

**HOST:**

"Before you can download gated models — and many of the best ones are gated — you need a Hugging Face account and token."

**[LIVE DEMO — Browser opens]**

```
1. Go to huggingface.co and create an account
2. Go to huggingface.co/settings/tokens
3. Create a 'Read' token (for downloading models)
4. For private model access or uploads, create a 'Write' token
```

**HOST:**

"Then authenticate from your terminal:"

```bash
# Install the HF CLI
pip install -U "huggingface_hub[cli]"

# Login with your token
huggingface-cli login
# Paste your token when prompted
# Token is stored in ~/.huggingface/token
```

"Let's test it:"

```python
from transformers import pipeline

# This downloads a small sentiment model and runs inference
classifier = pipeline("sentiment-analysis", 
                       model="distilbert-base-uncased-finetuned-sst-2-english")
result = classifier("I love setting up AI environments!")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9998}]
```

**HOST:**

"If you got a positive sentiment with 99.9% confidence, congratulations — your Hugging Face pipeline is working."

"Here's a pro tip: if you're on a machine with limited disk space, HF models cache in `~/.cache/huggingface/`. You can redirect that:"

```bash
# Set a custom cache location (e.g., an external drive)
export HF_HOME=/path/to/your/cache
export HF_HUB_CACHE=/path/to/your/cache/hub
```

"Now let's also install scipy and bitsandbytes — we'll need them for quantization later:"

```bash
# For 4-bit / 8-bit quantization (essential for running big models on consumer GPUs)
pip install bitsandbytes
pip install scipy
pip install peft          # Parameter-efficient fine-tuning (LoRA)
```

---

## OLLAMA: LOCAL MODELS

**[14:00–17:30]**

**HOST:**

"Ollama changed the game. It's the easiest way to run LLMs on your local machine. Think of it as Docker for models — one command to download, one command to run."

**[LIVE DEMO]**

```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Check if the Ollama service is running
ollama serve
# If it's already running, you'll get an error saying "address already in use"
# That's fine — it means it's working
```

**HOST:**

"Now let's pull some models. Start small:"

```bash
# Pull small models for testing (fast downloads)
ollama pull phi3:mini        # 3.8B parameters, ~2.3 GB
ollama pull llama3.2:1b      # 1B parameter, ~1.3 GB
ollama pull gemma2:2b        # 2B parameters, ~1.6 GB

# For serious work (download times vary):
ollama pull codellama:7b     # 7B parameter coding model, ~4.1 GB
ollama pull llama3.2:70b     # 70B parameter flagship, ~40 GB (needs serious VRAM)
```

"Let's test it in the terminal:"

```bash
# Run a model interactively
ollama run phi3:mini
# Type your prompt, hit enter
# Type /exit to quit

# Or get a single response
ollama run phi3:mini "Explain quantum computing in one sentence"
```

"Let's also pull the embedding model we'll use later:"

```bash
ollama pull nomic-embed-text   # For RAG, semantic search
```

**HOST:**

"The Python SDK is where it gets powerful. Let me show you:"

```bash
# Install the Ollama Python library
pip install ollama
```

```python
import ollama

# Generate a response
response = ollama.generate(
    model='phi3:mini',
    prompt='What is transfer learning in one paragraph?',
)
print(response['response'])

# Or use the chat interface (preserves conversation history)
response = ollama.chat(
    model='phi3:mini',
    messages=[
        {'role': 'user', 'content': 'What is the Far Side?'},
        {'role': 'assistant', 'content': 'The Far Side is a comic strip by Gary Larson.'},
        {'role': 'user', 'content': 'Why is it funny?'},
    ]
)
print(response['message']['content'])
```

"Here's how to use Ollama for embeddings — this is the building block for RAG:"

```python
import ollama

response = ollama.embeddings(
    model='nomic-embed-text',
    prompt='Hello world',
)
print(f"Embedding dimension: {len(response['embedding'])}")
# Should print: 768
```

**HOST:**

"One thing people miss: you can pull models from Ollama's Python API too:"

```python
import ollama
ollama.pull('codellama:7b')
print("Model downloaded successfully!")
```

---

## VLLM FOR HIGH-THROUGHPUT SERVARDING

**[17:30–21:00]**

**HOST:**

"Ollama is great for local development, but when you need production-grade serving — think high throughput, continuous batching, OpenAI-compatible API — vLLM is what you want."

"vLLM implements PagedAttention, which is a custom CUDA kernel that manages KV cache memory like an operating system manages virtual memory. The result? 2-4x faster throughput compared to vanilla Hugging Face serving."

**[LIVE DEMO]**

```bash
# Install vLLM
# Note: vLLM has strict requirements — CUDA 12.8 and PyTorch 2.6
# These need to match exactly
pip install vllm

# Or install with your existing PyTorch:
pip install vllm --no-cache-dir
```

"Let me show you my preferred approach — vLLM in Docker for clean isolation:"

```bash
# Using Docker (recommended for production)
docker run --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model microsoft/Phi-3-mini-4k-instruct \
    --trust-remote-code
```

"Or directly with Python:"

```python
from vllm import LLM, SamplingParams

# Initialize the model
llm = LLM(
    model="microsoft/Phi-3-mini-4k-instruct",
    trust_remote_code=True,
    dtype="auto",
    gpu_memory_utilization=0.9,
)

# Set sampling parameters
sampling_params = SamplingParams(
    temperature=0.7,
    max_tokens=256,
    top_p=0.95,
)

# Generate prompts
prompts = [
    "Write a haiku about machine learning",
    "Explain PagedAttention in one sentence",
]

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt[:50]}...")
    print(f"Generated: {output.outputs[0].text}")
    print("---")
```

"Here's the serving mode — gives you an OpenAI-compatible API endpoint:"

```bash
# Start an OpenAI-compatible server with vLLM
python -m vllm.entrypoints.openai.api_server \
    --model microsoft/Phi-3-mini-4k-instruct \
    --port 8000 \
    --trust-remote-code

# Test it like OpenAI:
curl http://localhost:8000/v1/models

curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "microsoft/Phi-3-mini-4k-instruct",
        "messages": [{"role": "user", "content": "Hello!"}],
        "max_tokens": 100
    }'
```

**HOST:**

"See that? It's an OpenAI-compatible API running on *your* hardware. No API bills. No rate limits. No data leaving your machine. Swap out OpenAI's endpoint URL for `http://localhost:8000/v1` in any project and it just works."

"The `gpu_memory_utilization=0.9` parameter tells vLLM to use 90% of your GPU memory for KV cache. Start at 0.8 if you get OOM errors and work up."

---

## IDE SETUP: CURSOR & VS CODE

**[21:00–24:00]**

**HOST:**

"Your IDE is your workshop. Let's set up the two I recommend for AI development."

**[LIVE DEMO — Cursor]**

```bash
# Install Cursor (AI-first IDE)
# Download from: https://www.cursor.com/
# Also available via snap:
sudo snap install cursor --classic

# Or on Mac:
brew install --cask cursor
```

**HOST:**

"Cursor is VS Code with AI baked in. Here's my recommended configuration:"

**Cursor Settings (`~/.config/Cursor/User/settings.json` or `settings.json` in-app):**

```json
{
  "editor.fontSize": 14,
  "editor.fontFamily": "'JetBrains Mono', 'Fira Code', monospace",
  "editor.tabSize": 2,
  "editor.wordWrap": "on",
  "editor.minimap.enabled": false,
  
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  
  "cursor.chat.enabled": true,
  
  "files.exclude": {
    "**/__pycache__": true,
    "**/.venv": false,
    "**/*.pyc": true,
    ".git": true
  }
}
```

"Now VS Code:"

**[LIVE DEMO — VS Code]**

```bash
# Install VS Code
sudo snap install code --classic

# Install essential extensions
code --install-extension ms-python.python
code --install-extension ms-python.pylint
code --install-extension ms-toolsai.jupyter
code --install-extension ms-azuretools.vscode-docker
code --install-extension eamodio.gitlens
code --install-extension grimcos.adjust-word-wrap
code --install-extension ms-python.black-formatter
code --install-extension charliermarsh.ruff
```

"My `settings.json` for VS Code AI work:"

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.analysis.typeCheckingMode": "basic",
  
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "ms-python.black-formatter",
  
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    },
    "editor.tabSize": 4,
    "editor.rulers": [88]
  },
  
  "ruff.lint.args": ["--config=pyproject.toml"],
  "jupyter.askForKernelRestart": false,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  },
  "terminal.integrated.env.linux": {
    "PYTHONDONTWRITEBYTECODE": "1"
  }
}
```

**HOST:**

"And `pyproject.toml` for reproducible linting config:"

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
target-version = "py311"
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
```

---

## API KEY MANAGEMENT & SECURITY

**[24:00–26:00]**

**HOST:**

"Your API keys are credentials. Treat them like passwords. Never hardcode them. Never commit them to git. Here's the professional approach."

**[LIVE DEMO]**

```bash
# Create a .env file in your project root
cat > .env << 'EOF'
# Hugging Face
HF_TOKEN=hf_YOUR_TOKEN_HERE

# OpenAI
OPENAI_API_KEY=sk-YOUR_KEY_HERE

# OpenRouter (alternative to OpenAI)
OPENROUTER_API_KEY=sk-or-YOUR_KEY_HERE

# Anthropic
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE

# Optional: Weights & Biases for experiment tracking
WANDB_API_KEY=your_wandb_key
EOF

# Make it read-only
chmod 600 .env

# CRITICAL: Make sure .env is in .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to .gitignore"
```

"Now load it in Python:"

```python
# pip install python-dotenv (put this in your requirements too)
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Use them
hf_token = os.getenv("HF_TOKEN")
openai_key = os.getenv("OPENAI_API_KEY")

if not hf_token:
    raise ValueError("HF_TOKEN not set! Check your .env file.")
```

"Here's a handy `load_keys.py` utility:"

```python
import os
from pathlib import Path
from dotenv import load_dotenv

def load_env(env_path: str = ".env") -> dict:
    """Load and validate environment variables from .env file."""
    env_file = Path(env_path)
    if not env_file.exists():
        print(f"WARNING: {env_path} not found!")
        return {}
    
    load_dotenv(env_file)
    
    keys = {
        "HF_TOKEN": os.getenv("HF_TOKEN", ""),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY", ""),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
    }
    
    missing = [k for k, v in keys.items() if not v]
    if missing:
        print(f"Missing keys: {', '.join(missing)}")
    else:
        print("All API keys loaded successfully!")
    
    return keys
```

**HOST:**

"One more thing — `pre-commit` hooks to prevent accidentally committing secrets:"

```bash
pip install pre-commit
pre-commit install

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Initialize the baseline
detect-secrets scan > .secrets.baseline
```

"Now if you try to commit a file with an API key, it'll block you before it happens."

---

## COST MONITORING & WRAP-UP

**[26:00–28:00]**

**HOST:**

"Last piece: knowing what your AI development actually costs. API fees add up fast."

"Here's a simple cost tracking approach:"

```python
# Simple API cost logger
import os
import json
from datetime import datetime
from pathlib import Path

COST_LOG = Path("~/.ai-dev/costs.json").expanduser()
COST_LOG.parent.mkdir(exist_ok=True)

COST_PER_TOKEN = {
    "gpt-4o": {"input": 0.0025 / 1000, "output": 0.01 / 1000},
    "gpt-4o-mini": {"input": 0.00015 / 1000, "output": 0.0006 / 1000},
    "claude-3.5-sonnet": {"input": 0.0003 / 1000, "output": 0.0015 / 1000},
    "default": {"input": 0.001 / 1000, "output": 0.002 / 1000},
}

def log_api_call(model: str, input_tokens: int, output_tokens: int):
    rates = COST_PER_TOKEN.get(model, COST_PER_TOKEN["default"])
    cost = (input_tokens * rates["input"]) + (output_tokens * rates["output"])
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost,
    }
    
    costs = json.loads(COST_LOG.read_text()) if COST_LOG.exists() else []
    costs.append(entry)
    COST_LOG.write_text(json.dumps(costs, indent=2))
    
    return cost

def get_monthly_summary():
    if not COST_LOG.exists():
        print("No cost data yet.")
        return
    
    costs = json.loads(COST_LOG.read_text())
    total = sum(e["cost_usd"] for e in costs)
    by_model = {}
    for e in costs:
        by_model[e["model"]] = by_model.get(e["model"], 0) + e["cost_usd"]
    
    print(f"Total spent: ${total:.4f}")
    for model, cost in sorted(by_model.items(), key=lambda x: -x[1]):
        print(f"  {model}: ${cost:.4f}")
```

**HOST:**

"And for GPU cloud costs — if you're spinning up instances:"

```
Quick reference (as of mid-2025):
  - T4 (16GB):        ~$0.35/hr  (fine-tuning small models)
  - A10G (24GB):      ~$1.00/hr  (fine-tuning 7B, inference 13B)
  - A100-40G:         ~$1.50/hr  (training anything)
  - H100 (80GB):      ~$2.50/hr  (production, large-scale)
  
  Lambda Cloud, Vast.ai, and RunPod offer spot pricing — 
  often 50-70% cheaper than on-demand.
```

---

## RECAP

**[27:00–28:00 — ON SCREEN: Summary checklist]**

"Let's recap everything we set up today:"

"""
  Python 3.11 + venv          — Isolated environments, no conflicts
  PyTorch 2.x + CUDA 12.4     — GPU-accelerated deep learning
  Hugging Face Transformers   — Access to thousands of pre-trained models
  Ollama                      — Local LLM inference, privacy-first
  vLLM                        — Production serving, OpenAI-compatible API
  Cursor + VS Code            — AI-first development workflow
  .env + python-dotenv        — Secure API key management
  pre-commit + detect-secrets — Protect against accidental secret commits
  Cost tracking               — Know exactly what your AI work costs
"""

"All the scripts from today are in the repo — `episode-04-dev-environment/`:"

```
SCRIPT.md                  — This script
src/01_setup_check.py      — Check what's installed on your system
src/02_create_venv.sh      — Automated environment setup
src/03_verify_install.py   — Verify everything works
```

"If you found this useful, subscribe. Episode 5 is where we start using all this — we'll build a complete retrieval-augmented generation system from scratch."

"The Far Side is where we skip the tutorial and start building. See you in the next one."

---

## EPISODE LINKS & RESOURCES

- Python: https://www.python.org/downloads/
- PyTorch Install: https://pytorch.org/get-started/locally/
- Hugging Face: https://huggingface.co/
- Ollama: https://ollama.com/
- vLLM: https://vllm.ai/
- Cursor: https://www.cursor.com/
- VS Code: https://code.visualstudio.com/
- python-dotenv: https://pypi.org/project/python-dotenv/

## FILES IN THIS EPISODE

```
episode-04-dev-environment/
  SCRIPT.md                  Video script (this file)
  src/
    01_setup_check.py        System requirements checker
    02_create_venv.sh        Automated venv + package installer
    03_verify_install.py     Post-install verification suite
```
