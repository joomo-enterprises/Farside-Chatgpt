#!/usr/bin/env python3
"""
Episode 1: Local Chat with Ollama Python API
A simple Python chat interface using the Ollama API.

Usage:
    pip install ollama
    python 01_local_chat.py
    python 01_local_chat.py --model mistral
"""

import sys
import json
import argparse

try:
    import ollama
except ImportError:
    print("Error: ollama package not installed.")
    print("Run: pip install ollama")
    sys.exit(1)


def chat(model: str, prompt: str) -> str:
    """Send a single prompt and return the response."""
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


def interactive_chat(model: str):
    """Run an interactive chat session."""
    print(f"Local Chat with {model}")
    print("Type 'quit' to exit, '/model <name>' to switch models")
    print("-" * 50)

    messages = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "/bye"):
            print("Goodbye!")
            break
        if user_input.startswith("/model "):
            model = user_input[7:].strip()
            print(f"Switched to model: {model}")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = ollama.chat(model=model, messages=messages)
            assistant_msg = response["message"]["content"]
            messages.append({"role": "assistant", "content": assistant_msg})
            print(f"\nAI: {assistant_msg}")
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure Ollama is running: ollama serve")


def main():
    parser = argparse.ArgumentParser(description="Local Chat with Ollama")
    parser.add_argument(
        "--model", type=str, default="mistral", help="Model name (default: mistral)"
    )
    parser.add_argument("--prompt", type=str, help="Single prompt (non-interactive mode)")
    args = parser.parse_args()

    if args.prompt:
        # Single prompt mode
        response = chat(args.model, args.prompt)
        print(response)
    else:
        # Interactive mode
        interactive_chat(args.model)


if __name__ == "__main__":
    main()
