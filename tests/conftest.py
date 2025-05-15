"""
Common test fixtures and configurations for pytest
"""

import os
import pytest
from fastapi.testclient import TestClient


# Test API key - this should be replaced with a real API key in production tests
TEST_GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "TEST_KEY_FOR_CI_ENVIRONMENT")

@pytest.fixture(scope="session")
def session_monkeypatch():
    m = pytest.MonkeyPatch()
    yield m
    m.undo()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(session_monkeypatch):
    """Set up test environment variables for the entire test session"""
    # Set environment to "test" for all tests
    session_monkeypatch.setenv("APP_ENVIRONMENT", "test")
    session_monkeypatch.setenv("TEST_GEMINI_API_KEY", TEST_GEMINI_API_KEY)
    session_monkeypatch.setenv("DEFAULT_MODEL", "gemini-1.5-flash")
    
    # Return environment info for debugging
    return {"environment": "test", "api_key": TEST_GEMINI_API_KEY}


@pytest.fixture(scope="session")
def test_client(setup_test_environment):
    """
    Create a test client for FastAPI application with test settings
    """
    # Now import the app - it will use our mocked settings during initialization
    from app.main import app

    client = TestClient(app)

    yield client

