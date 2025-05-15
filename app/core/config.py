"""
Configuration settings for the application
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings managed through environment variables"""

    def __init__(self, **kwargs):
        """Initialize settings based on environment"""
        # Set environment type from env var if not provided in kwargs
        env = kwargs.get("environment", os.environ.get("APP_ENVIRONMENT", "dev"))
        kwargs["environment"] = env

        # Call parent class initializer with environment-specific settings
        super().__init__(**kwargs)

        # Apply environment-specific overrides
        if env == "test":
            self._apply_test_settings()
        elif env == "prod":
            self._apply_prod_settings()

    # Environment type
    environment: str = Field(default="dev", description="Environment (test, dev, prod)")

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
    
    # Conversation context configuration
    context_window_size: int = Field(
        default=10, 
        description="Number of most recent messages to include in context window"
    )
    
    # MongoDB configuration
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017", 
        description="MongoDB connection URI"
    )
    mongodb_db_name: str = Field(
        default="ikkyu_san_chatbot", 
        description="MongoDB database name"
    )

    # API configuration
    api_prefix: str = Field(default="/api", description="API route prefix")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def _apply_test_settings(self):
        """Apply test environment specific settings"""
        # These overrides will be applied only in test environment
        # Override with test-specific settings
        test_api_key = os.environ.get(
            "TEST_GEMINI_API_KEY", "TEST_KEY_FOR_CI_ENVIRONMENT"
        )
        self.gemini_api_key = test_api_key
        self.mongodb_db_name = "ikkyu_san_test"

    def _apply_prod_settings(self):
        """Apply production environment specific settings"""
        # Production-specific overrides
        self.default_temperature = 0.5  # More deterministic in production


settings = Settings()