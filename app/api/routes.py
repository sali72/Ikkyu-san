"""
API routes for the chatbot application
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.llm.service import LLMService
from app.core.config import Settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.deps import get_llm_service, get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with the AI assistant",
    description="Send messages to the AI assistant and get a response",
)
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
    settings: Settings = Depends(get_settings),
):
    """
    Chat endpoint that processes user input and returns AI responses

    Args:
        request: Chat request with messages and optional parameters
        llm_service: LLM service for generating responses
        settings: Application settings

    Returns:
        AI assistant's response
    """
    try:
        # Use the provided system prompt or the default one
        system_prompt = request.system_prompt or settings.system_prompt

        # Generate response from LLM
        response = await llm_service.generate_response(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=system_prompt,
        )

        return ChatResponse(
            message=response["message"],
            usage=response["usage"],
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response from LLM service",
        )
