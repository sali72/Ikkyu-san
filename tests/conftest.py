"""
Common test fixtures and configurations for pytest
"""

from collections.abc import AsyncGenerator

import os
import pytest
from fastapi.testclient import TestClient
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession
from app.core.config import settings
from app.api.deps import get_db
from app.core.db import set_current_session
from app.models import Conversation

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


async def get_test_db_client():
    client = AsyncIOMotorClient(settings.mongodb_uri)
    await init_beanie(
        database=client[settings.mongodb_db_name], document_models=[Conversation]
    )
    return client


async def get_test_db_session() -> (
    AsyncGenerator[AsyncIOMotorClientSession, None, None]
):
    client = await get_test_db_client()
    async with await client.start_session() as session:
        set_current_session(session)
        yield session


@pytest.fixture(scope="session")
def test_client(setup_test_environment):
    """
    Create a test client for FastAPI application with test settings
    """
    # Now import the app - it will use our mocked settings during initialization
    from app.main import app

    app.dependency_overrides[get_db] = get_test_db_session
    with TestClient(app) as test_client:
        yield test_client
    
    
    # db_client = await get_test_db_client()
    # await db_client.drop_database(settings.mongodb_db_name)
