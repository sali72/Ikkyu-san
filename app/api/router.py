"""
Main API router for the chatbot application
"""

import logging
from fastapi import APIRouter

from app.api.routes.chat import router as chat_router
from app.api.routes.conversation import router as conversation_router

# Configure logging
logger = logging.getLogger(__name__)

# Create main router
router = APIRouter()

# Include the modular routers
router.include_router(chat_router, tags=["chat"])
router.include_router(conversation_router, tags=["conversations"])
