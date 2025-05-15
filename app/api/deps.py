"""
Dependency injection utilities for FastAPI
"""
from app.core.llm.service import LLMService

def get_llm_service() -> LLMService:
    """Dependency to get LLM service with settings"""
    return LLMService()
