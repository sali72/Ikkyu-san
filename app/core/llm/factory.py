"""
Factory for creating LLM providers
"""

from typing import Optional
from app.core.config import Settings
from app.core.llm.interface import LLMProvider

# Import all providers
from app.core.llm.providers.openrouter_provider import OpenRouterProvider
from app.core.llm.providers.gemini_provider import GeminiProvider



def create_llm_provider(
    provider_name: str, settings: Optional[Settings] = None
) -> LLMProvider:
    """
    Create an LLM provider based on the provider name

    Args:
        provider_name: Name of the provider to create
        settings: Application settings

    Returns:
        An instance of the specified LLM provider

    Raises:
        ValueError: If the provider name is not supported
    """
    settings = settings or Settings()

    providers = {
        "openrouter": OpenRouterProvider,
        "gemini": GeminiProvider,
    }

    if provider_name not in providers:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")

    return providers[provider_name](settings)
