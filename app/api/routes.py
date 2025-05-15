"""
API routes for the chatbot application
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path

from app.core.llm.service import LLMService
from app.crud import conversation as conversation_service
from app.core.config import settings
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationList,
    ConversationInfo,
    Message,
)
from app.api.deps import get_llm_service

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
        # Use the provided system prompt or the default one
        system_prompt = request.system_prompt or settings.system_prompt
        model = request.model or settings.default_model

        # Get or create conversation
        if request.conversation_id:
            conversation = await conversation_service.get_conversation(
                request.user_id, request.conversation_id
            )
            if not conversation:
                # If conversation not found, create a new one
                conversation = await conversation_service.create_conversation(
                    request.user_id, model=model
                )
        else:
            # Create a new conversation
            conversation = await conversation_service.create_conversation(
                request.user_id, model=model
            )

        # Get the latest user message
        user_message = request.messages[-1]

        # Save user message to conversation context
        await conversation_service.add_message(
            request.user_id, conversation.conversation_id, user_message
        )

        # Get context window for LLM
        context_messages = conversation_service.get_context_window(
            conversation.messages, system_prompt
        )

        # Generate response from LLM
        response = await llm_service.generate_response(
            messages=context_messages,
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=None,  # Already included in context_messages
        )

        # Save assistant response to conversation
        assistant_message = Message(
            role="assistant", content=response["message"]["content"]
        )

        # Add token usage to conversation if available
        token_count = 0
        if response.get("usage") and response["usage"].get("total_tokens"):
            token_count = response["usage"].get("total_tokens", 0)

        await conversation_service.add_message(
            request.user_id,
            conversation.conversation_id,
            assistant_message,
            token_count=token_count,
        )

        return ChatResponse(
            message=response["message"],
            usage=response["usage"],
            conversation_id=conversation.conversation_id,
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.exception("Full exception details:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response from LLM service",
        )


@router.get(
    "/conversations",
    response_model=ConversationList,
    status_code=status.HTTP_200_OK,
    summary="List user conversations",
    description="Get a list of conversations for the user",
)
async def list_conversations(
    user_id: str,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    """
    Get a list of conversations for a user

    Args:
        user_id: Unique identifier for the user
        limit: Maximum number of conversations to return
        skip: Number of conversations to skip

    Returns:
        List of conversation information
    """
    try:
        conversations = await conversation_service.list_conversations(
            user_id, limit, skip
        )

        # Convert to response format
        conversation_infos = [
            ConversationInfo(
                conversation_id=conv.conversation_id,
                title=conv.title,
                updated_at=conv.updated_at.isoformat(),
                model=conv.model,
                message_count=len(conv.messages),
            )
            for conv in conversations
        ]

        # Get total count (in a real app, this could be a separate optimized query)
        total = len(
            await conversation_service.list_conversations(user_id, limit=1000, skip=0)
        )

        return ConversationList(conversations=conversation_infos, total=total)
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations",
        )


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
    description="Delete a conversation by ID",
)
async def delete_conversation(
    conversation_id: str = Path(
        ..., description="Unique identifier for the conversation"
    ),
    user_id: str = Query(..., description="Unique identifier for the user"),
):
    """
    Delete a conversation

    Args:
        conversation_id: Unique identifier for the conversation
        user_id: Unique identifier for the user
    """
    success = await conversation_service.delete_conversation(user_id, conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found",
        )


@router.get(
    "/conversations/{conversation_id}",
    response_model=List[Message],
    status_code=status.HTTP_200_OK,
    summary="Get conversation messages",
    description="Get all messages in a conversation",
)
async def get_conversation_messages(
    conversation_id: str = Path(
        ..., description="Unique identifier for the conversation"
    ),
    user_id: str = Query(..., description="Unique identifier for the user"),
):
    """
    Get all messages in a conversation

    Args:
        conversation_id: Unique identifier for the conversation
        user_id: Unique identifier for the user

    Returns:
        List of messages in the conversation
    """
    conversation = await conversation_service.get_conversation(user_id, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found",
        )

    return conversation.messages
