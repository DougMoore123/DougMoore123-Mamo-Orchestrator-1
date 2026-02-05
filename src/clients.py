from __future__ import annotations

from openai import AzureOpenAI
from .config import Settings


def create_client(settings: Settings) -> AzureOpenAI:
    return AzureOpenAI(
        api_version=settings.api_version,
        azure_endpoint=settings.endpoint,
        api_key=settings.api_key,
    )
