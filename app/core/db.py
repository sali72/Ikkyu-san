"""
MongoDB client configuration using Motor and Beanie
"""

from functools import cache
import contextvars

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession as Session

# Context variable to store the current session
current_session = contextvars.ContextVar("db_session", default=None)

from app.core.config import settings
from app.models import Conversation


# Non-async function for creating the client
@cache
def create_motor_client():
    """Create and cache a MongoDB client - one per process."""
    if settings.db_mode == "local":
        return AsyncIOMotorClient(settings.mongodb_uri)
    elif settings.db_mode == "container":
        return AsyncIOMotorClient(settings.mongodb_docker_host)
    else:
        raise ValueError("Invalid DB mode")


# Async function for initialization
async def get_client():
    """Get the client and ensure Beanie is initialized."""
    client = create_motor_client()
    # Only initialize Beanie once per client
    if not hasattr(client, "_beanie_initialized"):
        await init_beanie(
            database=client[settings.mongodb_db_name], document_models=[Conversation]
        )
        client._beanie_initialized = True
    return client


def get_current_session() -> Session:
    """Get the current session from the context variable"""
    return current_session.get()


def set_current_session(session: Session) -> None:
    """Set the current session in the context variable"""
    current_session.set(session)
