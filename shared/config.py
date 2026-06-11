"""
shared/config.py — Configuration templates for On The FarSide Series code examples.

Copy this file and customize it for your local setup. Never commit
API keys or secrets to version control.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class APIConfig:
    """Configuration for API-based examples."""

    # OpenAI
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.environ.get("OPENAI_API_KEY")
    )
    openai_model: str = "gpt-4o"

    # Anthropic
    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY")
    )
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Google
    google_api_key: Optional[str] = field(
        default_factory=lambda: os.environ.get("GOOGLE_API_KEY")
    )
    google_model: str = "gemini-2.0-flash"

    # Hugging Face
    hf_token: Optional[str] = field(
        default_factory=lambda: os.environ.get("HF_TOKEN")
    )

    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"


@dataclass
class AppConfig:
    """General application configuration."""

    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    output_dir: str = "./output"
    max_retries: int = 3
    request_timeout: int = 30


# Default instances — import these in your code examples
api_config = APIConfig()
app_config = AppConfig()
