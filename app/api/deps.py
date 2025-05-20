"""
Dependency injection utilities for FastAPI
"""

from app.core.llm.service import LLMService
from app.core.db import get_client, set_current_session, Session
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)


def get_llm_service() -> LLMService:
    """Dependency to get LLM service with settings"""
    return LLMService()


async def get_db() -> AsyncGenerator[Session, None]:
    """
    Asynchronous generator dependency that yields a new MongoDB session.
    This pattern ensures that each API call or request operates in its own session.
    Also sets the session in the context variable for global access.
    """
    client = await get_client()
    async with await client.start_session() as session:
        # Store the session in the context variable
        set_current_session(session)
        yield session
