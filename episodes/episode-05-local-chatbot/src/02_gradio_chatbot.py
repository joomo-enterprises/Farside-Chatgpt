#!/usr/bin/env python3
"""
Gradio Web Chatbot — Episode 05: Your First Open-Source AI App

A Gradio-powered web chat interface with:
  - Multi-turn conversation history (memory)
  - Streaming token-by-token responses
  - Model selector dropdown
  - Temperature slider
  - Clear / New Chat button

Usage:
    pip install ollama gradio
    python 02_gradio_chatbot.py

    # Make sure Ollama is running:
    #   ollama serve
    #   ollama pull llama3.2

Then open the URL printed in the terminal (usually http://127.0.0.1:7860).
"""

import sys
import time

try:
    import ollama
except ImportError:
    print("\n[ERROR] The 'ollama' package is not installed.")
    print("Install it with: pip install ollama\n")
    sys.exit(1)

try:
    import gradio as gr
except ImportError:
    print("\n[ERROR] The 'gradio' package is not installed.")
    print("Install it with: pip install gradio\n")
    sys.exit(1)


# ── Configuration ───────────────────────────────────────────────────────────
DEFAULT_MODEL = "llama3.2"
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant running locally on the user's "
    "machine. Be concise and clear. If you don't know something, say so."
)
DEFAULT_TEMPERATURE = 0.7
MODEL_CHOICES = ["llama3.2", "llama3.2:1b", "mistral", "phi3", "gemma2", "codellama"]


def get_available_models() -> list[str]:
    """Return a list of models available in Ollama, or fallback defaults."""
    try:
        result = ollama.list()
        models = [m["name"] for m in result.get("models", [])]
        return models if models else [DEFAULT_MODEL]
    except Exception:
        return [DEFAULT_MODEL]


# ── Chat function (streaming) ───────────────────────────────────────────────
def stream_chat(
    message: str,
    history: list,
    model_name: str,
    temperature: float,
    system_prompt: str,
) -> str:
    """
    Streaming chat handler.

    Takes the user message, conversation history, model, temperature, and
    system prompt. Yields partial responses token-by-token for the Gradio
    streaming UI.

    Args:
        message: The user's new message.
        history: List of [user_msg, assistant_msg] pairs from Gradio.
        model_name: The Ollama model to use.
        temperature: Controls randomness (0.0 = deterministic, 2.0 = creative).
        system_prompt: Custom system prompt.

    Yields:
        Accumulated partial response strings.
    """
    if not message or not message.strip():
        yield ""
        return

    # Build the full message list with history
    messages = [{"role": "system", "content": system_prompt}]

    for user_msg, assistant_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": str(user_msg)})
        if assistant_msg:
            messages.append({"role": "assistant", "content": str(assistant_msg)})

    messages.append({"role": "user", "content": message})

    try:
        stream = ollama.chat(
            model=model_name,
            messages=messages,
            stream=True,
            options={
                "temperature": round(temperature, 2),
            },
        )

        partial_response = ""
        for chunk in stream:
            delta = chunk.get("message", {}).get("content", "")
            partial_response += delta
            yield partial_response

    except ollama.ResponseError as e:
        yield f"[Ollama Error] {str(e)}\n\nMake sure Ollama is running and '{model_name}' is pulled:\n  ollama serve\n  ollama pull {model_name}"
    except Exception as e:
        yield f"[Error] {str(e)}"


def clear_chat():
    """Clear the chat history and input."""
    return None, None, ""


def submit_message(
    message: str,
    history: list,
    model_name: str,
    temperature: float,
    system_prompt: str,
):
    """
    Non-streaming fallback handler (used if streaming isn't desired).
    Same interface as stream_chat but returns the full response at once.
    """
    if not message or not message.strip():
        return history or [], ""

    result = stream_chat(message, history or [], model_name, temperature, system_prompt)
    full_response = ""
    for partial in result:
        full_response = partial

    new_history = history or []
    new_history.append((message, full_response))
    return new_history, ""


# ── Build the Gradio UI ─────────────────────────────────────────────────────
def build_app() -> gr.Blocks:
    """Construct and return the Gradio Blocks application."""

    available_models = get_available_models()
    default = DEFAULT_MODEL if DEFAULT_MODEL in available_models else available_models[0]

    # Custom CSS for a polished look
    custom_css = """
    .gradio-container {font-family: 'Segoe UI', system-ui, sans-serif;}
    .chatbot {min-height: 450px;}
    footer {display: none !important;}
    """

    with gr.Blocks(
       title="FarSide Local Chatbot — Episode 05",
        theme=gr.themes.Soft(),
        css=custom_css,
    ) as app:

        # ── Header ──────────────────────────────────────────────────
        gr.Markdown(
            """
            # 🤖 FarSide Local Chatbot
            ## Episode 05 — Your First Open-Source AI App

            **100% local · No API keys · Your data stays on your machine**
            """
        )

        with gr.Row():
            # ── Left column: Chat interface ──────────────────────────
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=480,
                    show_copy_button=True,
                    bubble_full_width=False,
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        label="",
                        placeholder="Type your message here... (Press Enter to send)",
                        scale=6,
                        container=False,
                        autofocus=True,
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)

                with gr.Row():
                    clear_btn = gr.Button("🗑️ Clear Chat", variant="stop")

            # ── Right column: Settings ────────────────────────────────
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Settings")

                model_dropdown = gr.Dropdown(
                    choices=available_models,
                    value=default,
                    label="Model",
                    info="Select which model to use for responses.",
                )

                temp_slider = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=DEFAULT_TEMPERATURE,
                    step=0.1,
                    label="Temperature",
                    info="Lower = more focused. Higher = more creative.",
                )

                system_ta = gr.Textbox(
                    label="System Prompt",
                    value=DEFAULT_SYSTEM_PROMPT,
                    lines=5,
                    max_lines=10,
                    info="Instructions that guide the AI's behavior.",
                )

                gr.Markdown("---")
                gr.Markdown(
                    "#### Tips\n"
                    "- **Temperature 0.0–0.3**: Good for factual Q&A\n"
                    "- **Temperature 0.7–1.0**: Good for conversation\n"
                    "- **Temperature 1.0–2.0**: Good for creative writing\n"
                    "- Change the system prompt mid-chat to change AI behavior"
                )

        # ── Status footer ─────────────────────────────────────────────
        with gr.Row():
            status = gr.Markdown(
                f"*Connected to Ollama · Default model: **{default}***"
            )

        # ── Event handlers ────────────────────────────────────────────

        # Send via button click
        send_event = send_btn.click(
            fn=stream_chat,
            inputs=[msg_input, chatbot, model_dropdown, temp_slider, system_ta],
            outputs=[chatbot],
        ).then(
            fn=lambda: "",
            outputs=[msg_input],
        )

        # Send via Enter key
        enter_event = msg_input.submit(
            fn=stream_chat,
            inputs=[msg_input, chatbot, model_dropdown, temp_slider, system_ta],
            outputs=[chatbot],
        ).then(
            fn=lambda: "",
            outputs=[msg_input],
        )

        # Clear button
        clear_btn.click(
            fn=lambda: (None, None),
            outputs=[chatbot, msg_input],
        )

    return app


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    """Launch the Gradio web app."""
    print("=" * 60)
    print("  FarSide Local Chatbot — Episode 05")
    print("  Your First Open-Source AI App")
    print("=" * 60)
    print()

    # Check Ollama connectivity
    try:
        models = ollama.list()
        model_names = [m["name"] for m in models.get("models", [])]
        if model_names:
            print(f"✓ Ollama connected. Available models: {', '.join(model_names)}")
        else:
            print("⚠ Ollama is running but no models found.")
            print(f"  Pull a model: ollama pull {DEFAULT_MODEL}")
    except Exception:
        print("✗ Cannot connect to Ollama.")
        print("  Start Ollama first: ollama serve")
        print("  Then pull a model:  ollama pull llama3.2")
        print()

    print("  Launching Gradio interface...")
    print()

    app = build_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=True,
    )


if __name__ == "__main__":
    main()
