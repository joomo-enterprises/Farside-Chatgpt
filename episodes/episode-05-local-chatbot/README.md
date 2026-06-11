# Episode 05 — Local Chatbot

**YouTube Link:** https://www.youtube.com/watch?v=PLACEHOLDER *(coming soon)*

## Description

Run your own LLM locally! This episode shows how to set up and chat with open-source language models on your own hardware using Ollama and llama.cpp. We cover model selection, quantization, performance optimization, and how to build a simple chatbot interface that runs entirely offline.

## Timestamps

| Time | Topic |
|------|-------|
| 00:00 | Why run models locally? |
| 05:00 | Installing Ollama |
| 12:00 | Model selection and quantization |
| 20:00 | Llama 3.2 deep dive |
| 28:00 | Running your first local model |
| 36:00 | Building a chatbot with memory |
| 44:00 | Performance tips and benchmarks |

*(Timestamps are approximate and will be updated when the episode goes live.)*

## Prerequisites

- Python 3.10+
- 16GB+ RAM recommended (8GB minimum)
- Ollama installed (instructions in README)
- Basic Python and terminal knowledge

## How to Run

```bash
# Install Ollama: https://ollama.com/download

# Pull a model
ollama pull llama3.2

# Install Python dependencies
pip install -r requirements.txt

# Run the local chatbot
cd src/
python chatbot.py
```

## What You'll Learn

- How to install and use Ollama
- Model quantization explained
- Choosing the right model for your hardware
- Building a persistent chatbot with conversation memory
- Performance optimization techniques
