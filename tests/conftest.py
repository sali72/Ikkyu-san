"""
Common test fixtures and configurations for pytest
"""

import os
import pytest
import asyncio
from google import genai
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import Settings
from app.core.llm.providers.gemini_provider import GeminiProvider


# Test API key - this should be replaced with a real API key in production tests
# For CI/CD environments, use environment variables instead
TEST_GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "TEST_KEY_FOR_CI_ENVIRONMENT")


@pytest.fixture
def test_client():
    """
    Create a test client for FastAPI application
    """
    return TestClient(app)


@pytest.fixture
def e2e_settings():
    """
    Create settings for E2E tests with test API key
    """
    return Settings(
        llm_provider="gemini",
        gemini_api_key=TEST_GEMINI_API_KEY,
        default_model="gemini-2.0-flash",
        default_temperature=0.7,
        max_tokens=1000,
        system_prompt="You are a helpful AI assistant.",
        api_prefix="/api",
    )


@pytest.fixture
def check_gemini_connection():
    """
    Fixture to check if Gemini API is reachable
    """
    async def _check_connection():
        try:
            # Configure the client
            client = genai.Client(api_key=TEST_GEMINI_API_KEY)
            
            # Simple test to check connectivity - list models
            client.models.list()
            
            # If we get here, the connection is successful
            return True, "Connected to Gemini API successfully"
        except Exception as e:
            return False, f"Failed to connect to Gemini API: {str(e)}"
    
    # Run the async function
    return asyncio.run(_check_connection())


@pytest.fixture
def gemini_provider(e2e_settings):
    """
    Create a Gemini provider instance with test settings
    """
    return GeminiProvider(e2e_settings)
