from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    api_key: str
    endpoint: str
    api_version: str
    chat_model: str
    embed_model: str


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing {name} environment variable.")
    return value


def load_settings() -> Settings:
    return Settings(
        api_key=_require_env("AZURE_OPENAI_API_KEY"),
        endpoint=_require_env("AZURE_OPENAI_ENDPOINT"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        chat_model=_require_env("AZURE_OPENAI_CHAT_MODEL"),
        embed_model=_require_env("AZURE_OPENAI_EMBED_MODEL"),
    )
