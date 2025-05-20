"""
Chat-related API routes
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.llm.service import LLMService
from app.api.deps import get_llm_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import chat as chat_service
from app.api.deps import get_db

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
    dependencies=[Depends(get_db)],
)
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
):
    """
    Chat endpoint that processes user input and returns AI responses

    Args:
        request: Chat request with messages and optional parameters
        llm_service: LLM service for generating responses

    Returns:
        AI assistant's response with conversation ID
    """
    try:
        # Delegate processing to the service layer
        # Session is already available via context variable
        response_data = await chat_service.process_chat_request(request, llm_service)

        # Convert to response model
        return ChatResponse(
            message=response_data["message"],
            usage=response_data["usage"],
            conversation_id=response_data["conversation_id"],
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.exception("Full exception details:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response from LLM service",
        )
