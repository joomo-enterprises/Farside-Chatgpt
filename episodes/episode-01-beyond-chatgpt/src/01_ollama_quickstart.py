#!/usr/bin/env python3
"""
Episode 1: Ollama Quickstart
Install and run your first local AI model in 2 commands.

Usage:
    python 01_ollama_quickstart.py
    python 01_ollama_quickstart.py --model mistral
    python 01_ollama_quickstart.py --model llama3.2
    python 01_ollama_quickstart.py --model gemma3
"""

import subprocess
import sys
import argparse
import shutil


def check_ollama_installed() -> bool:
    """Check if ollama is available on PATH."""
    return shutil.which("ollama") is not None


def install_ollama():
    """Install Ollama using the official install script."""
    print("=" * 60)
    print("Installing Ollama...")
    print("=" * 60)
    try:
        subprocess.run(
            ["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"],
            shell=True,
            check=True,
        )
        print("\nOllama installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("\nFailed to install automatically.")
        print("Install manually: https://ollama.ai/download")
        return False


def pull_model(model: str) -> bool:
    """Pull a model from Ollama registry."""
    print(f"\nPulling model: {model}")
    print("This may take a few minutes depending on your connection...\n")
    try:
        subprocess.run(["ollama", "pull", model], check=True)
        print(f"\nModel '{model}' is ready!")
        return True
    except subprocess.CalledProcessError:
        print(f"\nFailed to pull model '{model}'.")
        return False


def chat_with_model(model: str):
    """Start an interactive chat session with the model."""
    print(f"\nStarting chat with {model}...")
    print("Type 'quit' or '/bye' to exit.\n")
    print("-" * 60)

    try:
        subprocess.run(["ollama", "run", model])
    except KeyboardInterrupt:
        print("\n\nChat session ended.")
    except subprocess.CalledProcessError:
        print(f"\nFailed to start chat with '{model}'.")


def list_models():
    """List all locally available models."""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("Could not list models. Is Ollama running?")


def main():
    parser = argparse.ArgumentParser(
        description="Ollama Quickstart — Run local AI in minutes"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="mistral",
        help="Model to pull (default: mistral). Options: mistral, llama3.2, gemma3, codellama",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Start interactive chat after pulling model",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List locally available models",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  Ollama Quickstart — On The FarSide Series, Episode 1")
    print("=" * 60)

    if args.list:
        list_models()
        return

    # Step 1: Check if Ollama is installed
    if not check_ollama_installed():
        print("\nOllama is not installed on this system.")
        response = input("Would you like to install it? (y/n): ").strip().lower()
        if response == "y":
            if not install_ollama():
                sys.exit(1)
        else:
            print("Skipping install. Get Ollama at: https://ollama.ai/download")
            sys.exit(0)
    else:
        print("\nOllama is already installed!")

    # Step 2: Pull the model
    print(f"\nModel selected: {args.model}")
    response = input(f"Pull '{args.model}' now? (y/n): ").strip().lower()
    if response == "y":
        if not pull_model(args.model):
            sys.exit(1)

    # Step 3: Optionally chat
    if args.chat:
        chat_with_model(args.model)
    else:
        response = input(f"\nStart chatting with {args.model}? (y/n): ").strip().lower()
        if response == "y":
            chat_with_model(args.model)

    print("\n" + "=" * 60)
    print("  You now have a LOCAL AI running. No API calls. No cloud.")
    print("  This is the first step beyond ChatGPT.")
    print("=" * 60)


if __name__ == "__main__":
    main()
