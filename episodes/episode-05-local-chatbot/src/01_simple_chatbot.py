#!/usr/bin/env python3
"""
Simple Terminal Chatbot — Episode 05: Your First Open-Source AI App

A terminal-based chatbot using the Ollama Python library.
Supports multi-turn conversation with history, colored output,
 and a customizable system prompt.

Usage:
    pip install ollama
    python 01_simple_chatbot.py

    # Make sure Ollama is running and you have a model pulled:
    #   ollama serve
    #   ollama pull llama3.2
"""

import sys
from datetime import datetime

try:
    import ollama
except ImportError:
    print("\n[ERROR] The 'ollama' package is not installed.")
    print("Install it with: pip install ollama\n")
    sys.exit(1)


# ── ANSI color helpers (no external dependencies) ──────────────────────────
class Color:
    """ANSI escape codes for colored terminal output."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"


def colored(text: str, color: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{color}{text}{Color.RESET}"


# ── Chatbot class ───────────────────────────────────────────────────────────
class TerminalChatbot:
    """A terminal-based chatbot with conversation history and colored output."""

    def __init__(
        self,
        model: str = "llama3.2",
        system_prompt: str = None,
    ):
        self.model = model
        self.messages: list[dict] = []

        if system_prompt is None:
            system_prompt = (
                "You are a helpful, friendly AI assistant running locally "
                "on the user's machine. Be concise, clear, and conversational. "
                "If you don't know something, say so honestly."
            )
        self.messages.append({"role": "system", "content": system_prompt})

        self._turn_count = 0

    # ── Public API ──────────────────────────────────────────────────────
    def chat(self, user_input: str) -> str:
        """Send a message and return the assistant's reply."""
        self.messages.append({"role": "user", "content": user_input})
        self._turn_count += 1

        response = ollama.chat(model=self.model, messages=self.messages)
        reply = response["message"]["content"]
        self.messages.append({"role": "assistant", "content": reply})

        return reply

    def reset(self):
        """Clear conversation history (keeps system prompt)."""
        self.messages = [self.messages[0]]
        self._turn_count = 0

    @property
    def history(self) -> list[dict]:
        """Return a copy of the conversation history."""
        return list(self.messages)

    @property
    def turn_count(self) -> int:
        return self._turn_count

    # ── Helpers ──────────────────────────────────────────────────────────
    def _format_timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")


# ── UI helpers ──────────────────────────────────────────────────────────────
BANNER = r"""
 ╔══════════════════════════════════════════════════════════════╗
 ║           🤖  Local AI Chatbot  —  Episode 05              ║
 ║      Your First Open-Source AI App: Building a Chatbot     ║
 ╚══════════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
Commands:
  /help          Show this help message
  /reset         Clear conversation history
  /history       Show full conversation so far
  /model <name>  Switch model (e.g. /model llama3.2)
  /temp <value>  Set temperature (not yet implemented)
  /quit or /q    Exit the chatbot
"""


def print_banner():
    print(colored(BANNER, Color.CYAN))
    print(colored("  Type /help for commands. Start chatting!\n", Color.GRAY))


def print_user(text: str):
    ts = datetime.now().strftime("%H:%M")
    print(colored(f"  ┌─ You [{ts}]", Color.GREEN))
    for line in text.splitlines():
        print(colored(f"  │  {line}", Color.GREEN))
    print(colored(f"  └─", Color.GRAY))


def print_assistant(text: str, model: str):
    ts = datetime.now().strftime("%H:%M")
    print(colored(f"  ┌─ {model} [{ts}]", Color.MAGENTA))
    for line in text.splitlines():
        print(colored(f"  │  {line}", Color.WHITE))
    print(colored(f"  └─", Color.GRAY))


def print_system(text: str):
    print(colored(f"  ⚙  {text}", Color.YELLOW))


def print_info(text: str):
    print(colored(f"  ℹ  {text}", Color.DIM))


# ── Main loop ───────────────────────────────────────────────────────────────
def main():
    """Run the terminal chatbot REPL."""

    # Determine model from CLI args or default
    model = "llama3.2"
    if len(sys.argv) > 1:
        model = sys.argv[1]

    bot = TerminalChatbot(model=model)
    print_banner()
    print_info(f"Model: {model}")
    print_info(f"System: {bot.messages[0]['content'][:80]}...")
    print()

    while True:
        try:
            raw = input(colored(" You › ", Color.BOLD + Color.GREEN)).strip()
        except (EOFError, KeyboardInterrupt):
            print(colored("\n\n  Goodbye! 👋\n", Color.CYAN))
            sys.exit(0)

        if not raw:
            continue

        # ── Slash commands ──────────────────────────────────────────────
        if raw.startswith("/"):
            parts = raw.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ("/quit", "/q"):
                print(colored("\n  Goodbye! 👋\n", Color.CYAN))
                sys.exit(0)

            elif cmd == "/help":
                print(colored(HELP_TEXT, Color.GRAY))
                continue

            elif cmd == "/reset":
                bot.reset()
                print_system("Conversation history cleared.")
                continue

            elif cmd == "/history":
                if len(bot.history) <= 1:
                    print_info("No conversation history yet.")
                    continue
                print(colored("\n  ── Conversation History ──\n", Color.BOLD))
                for msg in bot.history:
                    role = msg["role"].upper()
                    content = msg["content"]
                    if role == "SYSTEM":
                        continue  # Skip system prompt in history display
                    label_color = Color.GREEN if role == "USER" else Color.MAGENTA
                    print(colored(f"  [{role}]", label_color))
                    for line in content.splitlines():
                        print(f"    {line}")
                    print()
                continue

            elif cmd == "/model":
                if not arg:
                    print_system(f"Current model: {bot.model}")
                    print_info("Usage: /model <model_name>")
                else:
                    old_model = bot.model
                    bot.model = arg
                    print_system(f"Switched model: {old_model} → {arg}")
                continue

            else:
                print_system(f"Unknown command: {cmd}. Type /help for options.")
                continue

        # ── Regular chat ────────────────────────────────────────────────
        print_user(raw)

        try:
            reply = bot.chat(raw)
            print_assistant(reply, model=bot.model)
            print()  # Blank line between turns
        except ollama.ResponseError as e:
            print(colored(f"\n  [OLLAMA ERROR] {e}\n", Color.RED))
            print_info(f"Make sure Ollama is running and '{model}' is pulled:")
            print_info(f"  ollama serve")
            print_info(f"  ollama pull {model}\n")
        except Exception as e:
            print(colored(f"\n  [ERROR] {e}\n", Color.RED))
            print_info("Is Ollama running? Try: ollama serve\n")


if __name__ == "__main__":
    main()
