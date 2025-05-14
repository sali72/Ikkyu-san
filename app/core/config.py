"""
Configuration settings for the application
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings managed through environment variables"""

    # LLM provider configuration
    llm_provider: str = Field(
        default="gemini", description="LLM provider to use (openrouter, gemini)"
    )

    # API credentials for different providers
    openrouter_api_key: str = Field(
        default="", description="API key for OpenRouter LLM service"
    )
    gemini_api_key: str = Field(
        default="", description="API key for Google AI Studio Gemini service"
    )


    # LLM Configuration
    default_model: str = Field(
        default="gemini-2.0-flash", description="Default LLM model to use"
    )
    default_temperature: float = Field(
        default=0.7, description="Default temperature for LLM responses"
    )
    max_tokens: Optional[int] = Field(
        default=1000, description="Maximum number of tokens in LLM response"
    )
    system_prompt: str = Field(
        default="You are a helpful AI assistant.",
        description="Default system prompt for the LLM",
    )

    # API configuration
    api_prefix: str = Field(default="/api", description="API route prefix")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
