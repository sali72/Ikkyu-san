"""
Configuration settings for the application
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings managed through environment variables"""

    # API credentials for OpenRouter
    openrouter_api_key: str = Field(
        default="", description="API key for OpenRouter LLM service"
    )

    # LLM Configuration
    default_model: str = Field(
        default="openai/gpt-3.5-turbo", description="Default LLM model to use"
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
