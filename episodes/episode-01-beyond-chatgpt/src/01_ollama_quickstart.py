# Episode 1: Quick Start — Run AI Locally in 2 Commands

"""Install Ollama and run your first local AI model.
From Episode 1 of On The FarSide Series.
"""

import subprocess
import sys
import shutil


def check_ollama_installed() -> bool:
    """Check if Ollama is installed on this system."""
    return shutil.which("ollama") is not None


def install_ollama():
    """Install Ollama on Linux/macOS."""
    print("=" * 50)
    print("  Installing Ollama...")
    print("=" * 50)
    print()
    print("Ollama is not installed. Installing now...")
    print("(This downloads ~200MB, takes 1-2 minutes on fast connection)")
    print()

    result = subprocess.run(
        ["bash", "-c", "curl -fsSL https://ollama.ai/install.sh | sh"],
        capture_output=False
    )

    if result.returncode != 0:
        print("ERROR: Ollama installation failed.")
        print("Install manually: https://ollama.ai/download")
        sys.exit(1)

    print()
    print("Ollama installed successfully!")


def pull_model(model: str = "mistral"):
    """Pull an Ollama model."""
    print()
    print("=" * 50)
    print(f"  Pulling model: {model}")
    print("=" * 50)
    print()
    print(f"Downloading {model}... (this is a one-time ~4GB download)")
    print()

    result = subprocess.run(["ollama", "pull", model])

    if result.returncode != 0:
        print(f"ERROR: Failed to pull model '{model}'.")
        print("Try: ollama pull mistral")
        sys.exit(1)

    print()
    print(f"Model '{model}' ready!")


def run_local_chat(model: str = "mistral"):
    """Start an interactive local chat session."""
    print()
    print("=" * 50)
    print(f"  Starting local AI chat with {model}")
    print("=" * 50)
    print()
    print("Type your messages below. Type 'quit' to exit.")
    print()

    # Use the Ollama Python API for programmatic chat
    try:
        import ollama
    except ImportError:
        print("Installing ollama Python package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "ollama"],
                       capture_output=True)
        import ollama

    messages = []

    # Seed with a system message
    messages.append({
        "role": "system",
        "content": (
            "You are a helpful AI assistant running locally via Ollama. "
            "You are part of Episode 1 of On The FarSide Series, "
            "demonstrating local AI capabilities."
        )
    })

    print("─" * 50)
    print("  LOCAL AI CHAT — Running on YOUR machine")
    print("  No API key needed. No data leaves your computer.")
    print("─" * 50)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! You just ran AI locally. Welcome to the FarSide.")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = ollama.chat(model=model, messages=messages)
            reply = response["message"]["content"]
            messages.append({"role": "assistant", "content": reply})
            print(f"\nAI: {reply}\n")
        except Exception as e:
            print(f"\nERROR: {e}")
            print(f"Make sure Ollama is running: ollama serve")
            break

    return messages


def main():
    """Main entry point for Episode 1 demo."""
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║  On The FarSide Series — Episode 1              ║")
    print("║  Why Look Beyond ChatGPT in 2025                ║")
    print("║  Demo: Run AI Locally in 2 Commands             ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    model = "mistral"

    # Check if Ollama is installed
    if not check_ollama_installed():
        install_ollama()

    # Check if model is already pulled
    print(f"Checking if '{model}' model is available...")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10
        )
        model_available = model in result.stdout
    except Exception:
        model_available = False

    if not model_available:
        pull_model(model)
    else:
        print(f"Model '{model}' already available.")

    # Start the chat
    run_local_chat(model)


if __name__ == "__main__":
    main()
