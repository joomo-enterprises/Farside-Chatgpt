#!/usr/bin/env python3
"""
Episode 03: Multimodal AI Demo — Structuring API Calls
On The FarSide Series

Demonstrates how to structure multimodal API calls for:
- Text + Image (base64 encoded)
- Text + Audio (file path based)

Uses standard library only (no API keys needed — runs with mock responses).
Shows the exact request payload shapes you'd send to each provider.
"""

import base64
import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Data classes for structured request building
# ---------------------------------------------------------------------------

@dataclass
class ImageContent:
    """Represents an image to be sent to a multimodal API."""
    source: str  # "base64" or "file_path" or "url"
    data: str    # base64 string, file path, or URL
    mime_type: str = "image/png"

    def to_openai_format(self) -> dict:
        """Convert to OpenAI's expected image format."""
        if self.source == "base64":
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{self.mime_type};base64,{self.data}",
                    "detail": "high"
                }
            }
        elif self.source == "url":
            return {
                "type": "image_url",
                "image_url": {"url": self.data, "detail": "high"}
            }
        else:
            raise ValueError(f"OpenAI does not support source='{self.source}', use base64 or url")

    def to_gemini_format(self) -> dict:
        """Convert to Google Gemini's expected image format."""
        if self.source == "base64":
            return {
                "inline_data": {
                    "mime_type": self.mime_type,
                    "data": self.data
                }
            }
        elif self.source == "file_path":
            # Gemini API supports uploading files first, then referencing
            return {
                "file_data": {
                    "mime_type": self.mime_type,
                    "file_uri": f"gs://bucket/{os.path.basename(self.data)}"
                }
            }
        elif self.source == "url":
            return {
                "file_data": {
                    "mime_type": self.mime_type,
                    "file_uri": self.data
                }
            }
        else:
            raise ValueError(f"Unknown source: {self.source}")

    def to_claude_format(self) -> dict:
        """Convert to Anthropic Claude's expected image format."""
        if self.source == "base64":
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": self.mime_type,
                    "data": self.data
                }
            }
        elif self.source == "url":
            return {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": self.data
                }
            }
        else:
            raise ValueError(f"Claude does not support source='{self.source}', use base64 or url")


@dataclass
class AudioContent:
    """Represents audio to be sent to a multimodal API."""
    source: str  # "file_path" or "base64"
    data: str    # file path or base64 string
    mime_type: str = "audio/mp3"

    def to_openai_format(self) -> dict:
        """OpenAI audio is sent via the audio API, not the chat API."""
        if self.source == "base64":
            return {
                "type": "input_audio",
                "input_audio": {
                    "data": self.data,
                    "format": self.mime_type.split("/")[-1]  # mp3, wav, etc.
                }
            }
        else:
            raise ValueError("OpenAI chat completions expect base64 audio data")

    def to_gemini_format(self) -> dict:
        """Gemini supports inline audio data."""
        if self.source == "base64":
            return {
                "inline_data": {
                    "mime_type": self.mime_type,
                    "data": self.data
                }
            }
        elif self.source == "file_path":
            return {
                "file_data": {
                    "mime_type": self.mime_type,
                    "file_uri": f"gs://bucket/{os.path.basename(self.data)}"
                }
            }
        else:
            raise ValueError(f"Unknown source: {self.source}")


@dataclass
class TextContent:
    """Simple text content."""
    text: str

    def to_openai_format(self) -> dict:
        return {"type": "text", "text": self.text}

    def to_gemini_format(self) -> dict:
        return {"text": self.text}

    def to_claude_format(self) -> dict:
        return {"type": "text", "text": self.text}


@dataclass
class MultimodalMessage:
    """A single message that can contain text, images, and audio."""
    role: str = "user"
    contents: list = field(default_factory=list)

    def add_text(self, text: str) -> "MultimodalMessage":
        self.contents.append(TextContent(text))
        return self

    def add_image_base64(self, b64_data: str, mime_type: str = "image/png") -> "MultimodalMessage":
        self.contents.append(ImageContent(source="base64", data=b64_data, mime_type=mime_type))
        return self

    def add_image_url(self, url: str, mime_type: str = "image/png") -> "MultimodalMessage":
        self.contents.append(ImageContent(source="url", data=url, mime_type=mime_type))
        return self

    def add_audio_base64(self, b64_data: str, mime_type: str = "audio/mp3") -> "MultimodalMessage":
        self.contents.append(AudioContent(source="base64", data=b64_data, mime_type=mime_type))
        return self

    def to_openai_payload(self, model: str = "gpt-4o") -> dict:
        """Build the full OpenAI chat completions payload."""
        content_parts = []
        for c in self.contents:
            content_parts.append(c.to_openai_format())

        return {
            "model": model,
            "messages": [
                {
                    "role": self.role,
                    "content": content_parts
                }
            ],
            "max_tokens": 4096
        }

    def to_gemini_payload(self, model: str = "gemini-2.5-pro") -> dict:
        """Build the full Gemini payload."""
        parts = []
        for c in self.contents:
            parts.append(c.to_gemini_format())

        return {
            "contents": [
                {
                    "role": "user" if self.role == "user" else "model",
                    "parts": parts
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 4096,
                "temperature": 0.7
            }
        }

    def to_claude_payload(self, model: str = "claude-opus-4-1") -> dict:
        """Build the full Claude messages payload."""
        content_parts = []
        for c in self.contents:
            content_parts.append(c.to_claude_format())

        return {
            "model": model,
            "max_tokens": 4096,
            "messages": [
                {
                    "role": self.role,
                    "content": content_parts
                }
            ]
        }


# ---------------------------------------------------------------------------
# Mock API call simulator
# ---------------------------------------------------------------------------

class MockAPIResponse:
    """Simulates an API response for demonstration purposes."""

    def __init__(self, provider: str, model: str, request_payload: dict):
        self.provider = provider
        self.model = model
        self.request_payload = request_payload

    def generate_mock_response(self) -> dict:
        """Generate a realistic mock response based on the provider."""
        if self.provider == "openai":
            return {
                "id": "chatcmpl-mock123",
                "object": "chat.completion",
                "model": self.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "[GPT-4o Mock Response] I've analyzed the provided content. "
                                   "Based on the image and text, here is my analysis:\n\n"
                                   "1. The architecture shows a microservices pattern with clear separation.\n"
                                   "2. The primary bottleneck is the single database instance.\n"
                                   "3. Adding a caching layer would reduce database load by ~60%."
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 1250,
                    "completion_tokens": 87,
                    "total_tokens": 1337
                }
            }
        elif self.provider == "gemini":
            return {
                "candidates": [{
                    "content": {
                        "role": "model",
                        "parts": [{
                            "text": "[Gemini 2.5 Pro Mock Response] After analyzing the provided "
                                    "architecture diagram, I've identified the following:\n\n"
                                    "1. Database bottleneck: Single PostgreSQL instance handling all writes.\n"
                                    "2. No caching layer: Every request hits the database directly.\n"
                                    "3. Message queue: Single RabbitMQ instance could become a SPOF.\n\n"
                                    "Recommendations: Consider read replicas, Redis caching, and "
                                    "Kafka for event streaming at scale."
                        }]
                    },
                    "finishReason": "STOP"
                }],
                "usageMetadata": {
                    "promptTokenCount": 1100,
                    "candidatesTokenCount": 120,
                    "totalTokenCount": 1220
                }
            }
        elif self.provider == "claude":
            return {
                "id": "msg_mock456",
                "type": "message",
                "role": "assistant",
                "model": self.model,
                "content": [{
                    "type": "text",
                    "text": "[Claude Opus 4.1 Mock Response] Let me work through this systematically.\n\n"
                    "Step 1: Data flow analysis\n"
                    "  - Requests enter through the load balancer (2 instances, good)\n"
                    "  - Services communicate synchronously via REST (potential issue)\n\n"
                    "Step 2: Bottleneck identification\n"
                    "  - The database is the critical bottleneck. All 8 services write to one instance.\n"
                    "  - The service mesh configuration shows a potential race condition in the\n"
                    "    order-processing service — two services can simultaneously update order status.\n\n"
                    "Step 3: Prioritized recommendations\n"
                    "  1. (Critical) Fix the race condition — add optimistic locking or a saga pattern.\n"
                    "  2. (High) Split the database — separate read/write paths with CQRS.\n"
                    "  3. (Medium) Add Redis caching for the product catalog (read-heavy, rarely changes).\n"
                    "  4. (Medium) Replace synchronous REST calls with async messaging for non-critical paths."
                }],
                "stop_reason": "end_turn",
                "usage": {
                    "input_tokens": 1350,
                    "output_tokens": 195
                }
            }
        else:
            return {"error": f"Unknown provider: {self.provider}"}


def simulate_api_call(provider: str, model: str, payload: dict) -> dict:
    """Simulate an API call and return a mock response."""
    response = MockAPIResponse(provider, model, payload)
    return response.generate_mock_response()


# ---------------------------------------------------------------------------
# Demo scenarios
# ---------------------------------------------------------------------------

def create_sample_image_base64() -> str:
    """Create a minimal valid PNG image as base64 (1x1 pixel, orange)."""
    # Minimal PNG: 1x1 orange pixel (matches brand color)
    raw = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53, 0xDE,  # 8-bit RGB
        0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41, 0x54,  # IDAT chunk
        0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00, 0x00,  # compressed data
        0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC, 0x33,  # checksum
        0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,  # IEND chunk
        0xAE, 0x42, 0x60, 0x82  # IEND CRC
    ])
    return base64.b64encode(raw).decode("utf-8")


def create_sample_audio_base64() -> str:
    """Create a minimal valid WAV header as base64 (silence)."""
    # Minimal WAV: 1 second of silence, 16-bit mono 16kHz
    import struct
    sample_rate = 16000
    num_samples = sample_rate  # 1 second
    data = b'\x00\x00' * num_samples  # silence

    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + len(data),
        b'WAVE',
        b'fmt ',
        16,           # chunk size
        1,            # PCM format
        1,            # mono
        sample_rate,
        sample_rate * 2,  # byte rate
        2,            # block align
        16,           # bits per sample
        b'data',
        len(data)
    )
    return base64.b64encode(header + data).decode("utf-8")


def demo_text_and_image():
    """Demo: Send text + image to all three providers."""
    print_section("DEMO 1: Text + Image Analysis")
    print("Prompt: 'Analyze this system architecture diagram and identify bottlenecks.'")
    print("Image: 1x1 orange pixel (placeholder for architecture diagram)")
    print()

    b64_image = create_sample_image_base64()

    # Build the multimodal message
    msg = MultimodalMessage(role="user")
    msg.add_text("Analyze this system architecture diagram and identify the top 3 scalability bottlenecks.")
    msg.add_image_base64(b64_image, mime_type="image/png")

    # --- OpenAI ---
    print_subsection("OpenAI GPT-4o")
    payload = msg.to_openai_payload("gpt-4o")
    print(f"  Endpoint: https://api.openai.com/v1/chat/completions")
    print(f"  Payload keys: {list(payload.keys())}")
    print(f"  Content parts: {len(payload['messages'][0]['content'])}")
    for i, part in enumerate(payload['messages'][0]['content']):
        ptype = part.get('type', 'unknown')
        if ptype == 'image_url':
            url = part['image_url']['url']
            print(f"    Part {i}: {ptype} ({url[:60]}...)")
        else:
            text = part.get('text', '')[:60]
            print(f"    Part {i}: {ptype} (\"{text}...\")")

    response = simulate_api_call("openai", "gpt-4o", payload)
    content = response['choices'][0]['message']['content']
    usage = response['usage']
    print(f"  Response: {content[:80]}...")
    print(f"  Tokens: {usage['prompt_tokens']} in, {usage['completion_tokens']} out")
    print()

    # --- Gemini ---
    print_subsection("Google Gemini 2.5 Pro")
    payload = msg.to_gemini_payload("gemini-2.5-pro")
    print(f"  Endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent")
    print(f"  Payload keys: {list(payload.keys())}")
    parts = payload['contents'][0]['parts']
    print(f"  Parts: {len(parts)}")
    for i, part in enumerate(parts):
        if 'text' in part:
            print(f"    Part {i}: text (\"{part['text'][:60]}...\")")
        elif 'inline_data' in part:
            mime = part['inline_data']['mime_type']
            data_len = len(part['inline_data']['data'])
            print(f"    Part {i}: inline_data ({mime}, {data_len} chars base64)")

    response = simulate_api_call("gemini", "gemini-2.5-pro", payload)
    content = response['candidates'][0]['content']['parts'][0]['text']
    usage = response['usageMetadata']
    print(f"  Response: {content[:80]}...")
    print(f"  Tokens: {usage['promptTokenCount']} in, {usage['candidatesTokenCount']} out")
    print()

    # --- Claude ---
    print_subsection("Anthropic Claude Opus 4.1")
    payload = msg.to_claude_payload("claude-opus-4-1")
    print(f"  Endpoint: https://api.anthropic.com/v1/messages")
    print(f"  Payload keys: {list(payload.keys())}")
    content_parts = payload['messages'][0]['content']
    print(f"  Content parts: {len(content_parts)}")
    for i, part in enumerate(content_parts):
        ptype = part.get('type', 'unknown')
        if ptype == 'image':
            src = part['source']
            data_len = len(src.get('data', ''))
            print(f"    Part {i}: {ptype} ({src['type']}, {src['media_type']}, {data_len} chars)")
        else:
            text = part.get('text', '')[:60]
            print(f"    Part {i}: {ptype} (\"{text}...\")")

    response = simulate_api_call("claude", "claude-opus-4-1", payload)
    content = response['content'][0]['text'] if isinstance(response['content'], list) else response['content']
    usage = response['usage']
    print(f"  Response: {content[:80]}...")
    print(f"  Tokens: {usage['input_tokens']} in, {usage['output_tokens']} out")
    print()


def demo_text_and_audio():
    """Demo: Send text + audio to OpenAI and Gemini (Claude has no audio API)."""
    print_section("DEMO 2: Text + Audio Processing")
    print("Prompt: 'Summarize the key points from this audio recording.'")
    print("Audio: 1 second of silence (placeholder)")
    print()

    b64_audio = create_sample_audio_base64()

    # Build the multimodal message
    msg = MultimodalMessage(role="user")
    msg.add_text("Summarize the key points from this audio recording.")
    msg.add_audio_base64(b64_audio, mime_type="audio/wav")

    # --- OpenAI ---
    print_subsection("OpenAI GPT-4o (Audio)")
    payload = msg.to_openai_payload("gpt-4o")
    print(f"  Endpoint: https://api.openai.com/v1/chat/completions")
    print(f"  Content parts: {len(payload['messages'][0]['content'])}")
    for i, part in enumerate(payload['messages'][0]['content']):
        ptype = part.get('type', 'unknown')
        if ptype == 'input_audio':
            fmt = part['input_audio']['format']
            data_len = len(part['input_audio']['data'])
            print(f"    Part {i}: {ptype} (format={fmt}, {data_len} chars base64)")
        else:
            text = part.get('text', '')[:60]
            print(f"    Part {i}: {ptype} (\"{text}...\")")

    response = simulate_api_call("openai", "gpt-4o", payload)
    content = response['choices'][0]['message']['content']
    print(f"  Response: {content[:80]}...")
    print()

    # --- Gemini ---
    print_subsection("Google Gemini 2.5 Pro (Audio)")
    payload = msg.to_gemini_payload("gemini-2.5-pro")
    print(f"  Endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent")
    parts = payload['contents'][0]['parts']
    print(f"  Parts: {len(parts)}")
    for i, part in enumerate(parts):
        if 'text' in part:
            print(f"    Part {i}: text (\"{part['text'][:60]}...\")")
        elif 'inline_data' in part:
            mime = part['inline_data']['mime_type']
            data_len = len(part['inline_data']['data'])
            print(f"    Part {i}: inline_data ({mime}, {data_len} chars base64)")

    response = simulate_api_call("gemini", "gemini-2.5-pro", payload)
    content = response['candidates'][0]['content']['parts'][0]['text']
    print(f"  Response: {content[:80]}...")
    print()

    # --- Claude (no audio) ---
    print_subsection("Anthropic Claude Opus 4.1 (Audio)")
    print("  STATUS: No native audio API available.")
    print("  Workaround: Use a separate speech-to-text service (e.g., Whisper)")
    print("  to transcribe audio first, then send text to Claude.")
    print()


def demo_full_comparison():
    """Demo: Same prompt sent to all three, showing the full JSON payloads."""
    print_section("DEMO 3: Full Payload Comparison (Same Prompt)")
    print("Prompt: 'What do you see in this image?' + 1x1 orange pixel")
    print()

    b64_image = create_sample_image_base64()
    msg = MultimodalMessage(role="user")
    msg.add_text("What do you see in this image?")
    msg.add_image_base64(b64_image, mime_type="image/png")

    # Show full payloads
    for provider, model, method in [
        ("openai", "gpt-4o", "to_openai_payload"),
        ("gemini", "gemini-2.5-pro", "to_gemini_payload"),
        ("claude", "claude-opus-4-1", "to_claude_payload"),
    ]:
        print_subsection(f"{provider.upper()} — Full JSON Payload")
        payload = getattr(msg, method)(model)
        print(json.dumps(payload, indent=2, default=str)[:800])
        if len(json.dumps(payload, default=str)) > 800:
            print("  ... (truncated)")
        print()


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def print_section(title: str):
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_subsection(title: str):
    print(f"  --- {title} ---")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("  ╔══════════════════════════════════════════════════════════════════════╗")
    print("  ║       MULTIMODAL AI DEMO — API Call Structures                     ║")
    print("  ║       GPT-4o vs Gemini 2.5 Pro vs Claude Opus 4.1                  ║")
    print("  ║       On The FarSide Series — Episode 03                            ║")
    print("  ╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print("  This demo shows how to structure multimodal API calls using")
    print("  standard library only. All responses are mocked — no API keys needed.")
    print()

    demo_text_and_image()
    demo_text_and_audio()
    demo_full_comparison()

    # Summary
    print_section("KEY TAKEAWAYS")
    print()
    print("  1. Each provider has a DIFFERENT payload format for multimodal input:")
    print("     - OpenAI: content array with type='image_url' or type='input_audio'")
    print("     - Gemini: parts array with inline_data or file_data")
    print("     - Claude: content array with type='image' and source object")
    print()
    print("  2. Image encoding:")
    print("     - All three accept base64-encoded images")
    print("     - OpenAI and Gemini also accept URLs")
    print("     - Gemini additionally supports Google Storage URIs")
    print()
    print("  3. Audio support:")
    print("     - GPT-4o: Native real-time audio in chat completions")
    print("     - Gemini: Inline audio data in generateContent")
    print("     - Claude: No native audio — transcribe first, then send text")
    print()
    print("  4. Token counting differs:")
    print("     - Images are tokenized differently per provider")
    print("     - Audio tokenization varies by sample rate and duration")
    print("     - Always check the provider's token counting docs")
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
