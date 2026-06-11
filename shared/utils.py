"""
shared/utils.py — Common helper functions for On The FarSide Series code examples.

These utilities are shared across multiple episode modules to reduce
duplication and provide consistent patterns for API calls, data loading,
and output formatting.
"""

import os
import json
import time
from typing import Any, Optional


def load_json(path: str) -> dict:
    """Load a JSON file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, path: str, indent: int = 2) -> None:
    """Save data to a JSON file with pretty printing."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def timer(func):
    """Decorator that prints the execution time of a function."""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def ensure_dir(path: str) -> str:
    """Create a directory if it doesn't exist and return the path."""
    os.makedirs(path, exist_ok=True)
    return path


def get_env_or_raise(key: str) -> str:
    """Get an environment variable or raise a clear error."""
    value = os.environ.get(key)
    if value is None:
        raise EnvironmentError(
            f"Missing required environment variable: {key}. "
            f"Set it with: export {key}=your_value"
        )
    return value


def truncate(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max_length characters."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def print_header(title: str, char: str = "=", width: int = 60) -> None:
    """Print a formatted section header."""
    print()
    print(char * width)
    print(f" {title}")
    print(char * width)
