"""
Main application module for the AI chatbot backend
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.deps import get_settings

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
    settings = get_settings()
    logger.info(f"API configured with prefix: {settings.api_prefix}")
    logger.info(f"Using LLM model: {settings.default_model}")

    application = FastAPI(
        title="Ikkyu-san AI Chatbot",
        description="AI Chatbot backend powered by LLM APIs",
        version="0.1.0",
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development. In production, specify domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers with prefix from settings
    application.include_router(api_router, prefix=settings.api_prefix)

    return application


app = create_application()


@app.get("/")
async def root():
    """Root endpoint to check if the API is running"""
    return {"message": "Welcome to Ikkyu-san AI Chatbot API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
