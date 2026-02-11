"""Configurable settings for the Product Description Generator."""

import os
from dataclasses import dataclass, field


def _env_api_key() -> str:
    return os.environ.get("OPENAI_API_KEY", "your-api-key-here")


@dataclass
class AppConfig:
    api_key: str = field(default_factory=_env_api_key)
    model: str = "gpt-4"
    input_file: str = "products.json"
    output_file: str = "results.json"
