"""
Service layer for chat-related business logic
"""

import logging
from typing import Dict, Any

from app.core.config import settings
from app.core.llm.service import LLMService
from app.schemas.chat import Message, ChatRequest
from app.services import conversation as conversation_service

logger = logging.getLogger(__name__)


async def process_chat_request(
    request: ChatRequest, llm_service: LLMService
) -> Dict[str, Any]:
    """
    Process a chat request and generate a response

    Args:
        request: Chat request with messages and parameters
        llm_service: LLM service for generating responses

    Returns:
        Dict containing response data with message, usage info, and conversation ID
    """
    # Get model and system prompt
    model = request.model or settings.default_model

    # Get or create conversation
    conversation = await conversation_service.get_or_create_conversation(
        request.user_id, request.conversation_id or "", model
    )

    # Process user message
    updated_conversation = await process_user_message(request, conversation)

    # Generate LLM response
    response = await generate_llm_response(request, updated_conversation, llm_service)

    # Save assistant response
    await save_assistant_response(request, response, conversation.conversation_id)

    # Return formatted response
    return {
        "message": response["message"],
        "usage": response["usage"],
        "conversation_id": conversation.conversation_id,
    }


async def process_user_message(request: ChatRequest, conversation):
    """
    Process and save a user message

    Args:
        request: Chat request with the user message
        conversation: Conversation to add the message to

    Returns:
        Updated conversation with the user message added
    """
    # Get the latest user message
    user_message = request.messages[-1]

    # Save user message to conversation
    return await conversation_service.add_message(
        request.user_id, conversation.conversation_id, user_message
    )


async def generate_llm_response(
    request: ChatRequest, conversation, llm_service: LLMService
):
    """
    Generate a response from the LLM

    Args:
        request: Chat request with parameters
        conversation: Conversation with context
        llm_service: LLM service for generating responses

    Returns:
        Response from the LLM
    """
    # Get model and system prompt
    model = request.model or settings.default_model
    system_prompt = request.system_prompt or settings.system_prompt

    # Get context window for LLM
    context_messages = conversation_service.get_context_window(
        conversation.messages, system_prompt
    )
    logger.info(f"Context messages: {context_messages}")
    logger.info(f"System prompt: {system_prompt}")

    # Generate response from LLM
    return await llm_service.generate_response(
        messages=context_messages,
        model=model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )


async def save_assistant_response(request: ChatRequest, response, conversation_id: str):
    """
    Save the assistant's response to the conversation

    Args:
        request: Original chat request
        response: LLM response to save
        conversation_id: ID of the conversation

    Returns:
        Updated conversation with assistant response added
    """
    # Create assistant message
    assistant_message = Message(
        role="assistant", content=response["message"]["content"]
    )

    # Calculate token count
    token_count = 0
    if response.get("usage") and response["usage"].get("total_tokens"):
        token_count = response["usage"].get("total_tokens", 0)

    # Save to conversation
    return await conversation_service.add_message(
        request.user_id,
        conversation_id,
        assistant_message,
        token_count=token_count,
    )
