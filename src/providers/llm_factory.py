"""LLM Factory to instantiate the chosen provider."""

import os
from config.config import settings
from src.providers.base_client import BaseLLMClient
from src.providers.cloud_client import CloudLLMClient
from src.providers.mock_client import MockSimulatedLLMClient

def get_llm_client(provider: str = None) -> BaseLLMClient:
    """Returns the configured LLM client instance."""
    provider_name = (provider or settings.LLM_PROVIDER).lower()

    if provider_name == "mock":
        return MockSimulatedLLMClient()
    elif provider_name in ["openai", "anthropic", "gemini"]:
        return CloudLLMClient(provider=provider_name)
    else:
        # Default fallback
        return MockSimulatedLLMClient()
