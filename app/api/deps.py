"""
Dependency injection utilities for FastAPI
"""

from functools import lru_cache
from fastapi import Depends

from app.core.config import Settings
from app.core.llm.service import LLMService


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    The lru_cache ensures settings are loaded only once and reused.
    """
    return Settings()


# Dependency for LLM service
def get_llm_service(settings: Settings = Depends(get_settings)) -> LLMService:
    """Dependency to get LLM service with settings"""
    return LLMService(settings)
