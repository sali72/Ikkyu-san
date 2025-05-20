"""
Main application module for the AI chatbot backend
"""

import logging
from fastapi import FastAPI
from app.api.router import router as api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    Creates and configures the FastAPI application
    """
    logger.info(f"API configured with prefix: {settings.api_prefix}")
    logger.info(f"Using LLM model: {settings.default_model}")

    application = FastAPI(
        title="Ikkyu-san AI Chatbot",
        description="AI Chatbot backend powered by LLM APIs",
        version="0.1.0",
    )

    application.include_router(api_router, prefix=settings.api_prefix)

    return application


app = create_application()


@app.get("/")
async def root():
    """Root endpoint to check if the API is running"""
    return {"message": "Welcome to Ikkyu-san AI Chatbot API"}
