"""
MongoDB client configuration using Motor and Beanie
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.models import Conversation

logger = logging.getLogger(__name__)


async def init_database() -> None:
    """
    Initialize the database connection and register document models
    """
    try:
        # Create Motor client
        client = AsyncIOMotorClient(settings.mongodb_uri)
        
        # Initialize Beanie with the document models
        await init_beanie(
            database=client[settings.mongodb_db_name],
            document_models=[Conversation]
        )
        
        logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise 