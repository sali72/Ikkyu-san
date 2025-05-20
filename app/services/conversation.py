"""
Service layer for conversation-related business logic
"""

import logging
from typing import List, Dict, Any, Optional

from app.crud import conversation as conversation_crud
from app.core.config import settings
from app.schemas.chat import Message

logger = logging.getLogger(__name__)


async def get_conversation(
    user_id: str,
    conversation_id: str,
):
    """
    Get a conversation by ID

    Args:
        user_id: User ID
        conversation_id: Conversation ID

    Returns:
        Conversation object or None if not found
    """
    return await conversation_crud.get_conversation(user_id, conversation_id)


async def create_conversation(
    user_id: str,
    title: Optional[str] = None,
    model: Optional[str] = None,
):
    """
    Create a new conversation

    Args:
        user_id: User ID
        title: Optional title for the conversation
        model: Optional model name

    Returns:
        Newly created conversation
    """
    return await conversation_crud.create_conversation(user_id, title, model)


async def get_or_create_conversation(
    user_id: str,
    conversation_id: str,
    model: Optional[str] = None,
):
    """
    Get an existing conversation or create a new one if it doesn't exist

    Args:
        user_id: User ID
        conversation_id: Conversation ID
        model: Optional model name for new conversations

    Returns:
        Conversation object
    """
    conversation = await get_conversation(user_id, conversation_id)

    if not conversation:
        logger.warning(
            f"Conversation {conversation_id} not found for user {user_id}, creating new one"
        )
        conversation = await create_conversation(user_id, model=model)

    return conversation


async def add_message(
    user_id: str,
    conversation_id: str,
    message: Message,
    token_count: int = 0,
):
    """
    Add a message to a conversation

    Args:
        user_id: User ID
        conversation_id: Conversation ID
        message: Message to add
        token_count: Token count for the message

    Returns:
        Updated conversation with the message added
    """
    conversation = await get_or_create_conversation(
        user_id, conversation_id, settings.default_model
    )

    # Add message to conversation via CRUD layer
    return await conversation_crud.add_message(
        user_id, conversation.conversation_id, message, token_count
    )


async def list_conversations(
    user_id: str,
    limit: int = 10,
    skip: int = 0,
):
    """
    List conversations for a user

    Args:
        user_id: User ID
        limit: Max number of results
        skip: Number of results to skip

    Returns:
        List of conversations
    """
    return await conversation_crud.list_conversations(user_id, limit, skip)


async def delete_conversation(
    user_id: str,
    conversation_id: str,
):
    """
    Delete a conversation

    Args:
        user_id: User ID
        conversation_id: Conversation ID to delete

    Returns:
        True if deleted, False if not found
    """
    return await conversation_crud.delete_conversation(user_id, conversation_id)


def get_context_window(
    messages: List[Message], system_prompt: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get the context window for the LLM based on conversation history

    Args:
        messages: Full message history
        system_prompt: Optional system prompt to include

    Returns:
        List of messages formatted for the LLM within token constraints
    """
    # Initialize context with system prompt if provided
    context = _create_initial_context(system_prompt)

    # Get recent messages that fit within the context window
    recent_messages = _get_recent_messages(messages)

    # Add formatted messages to the context
    _add_messages_to_context(context, recent_messages)

    return context


def _create_initial_context(
    system_prompt: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Create the initial context with an optional system prompt"""
    context = []
    if system_prompt:
        context.append({"role": "system", "content": system_prompt})
    return context


def _get_recent_messages(messages: List[Message]) -> List[Message]:
    """Get the most recent messages that fit within the context window"""
    if len(messages) > settings.context_window_size:
        return messages[-settings.context_window_size :]
    return messages


def _add_messages_to_context(
    context: List[Dict[str, Any]], messages: List[Message]
) -> None:
    """Add messages to the context in the format expected by the LLM"""
    for message in messages:
        context.append({"role": message.role, "content": message.content})


def generate_title_from_message(content: str) -> str:
    """Generate a title from the message content"""
    max_title_length = 30
    if len(content) > max_title_length:
        return content[:max_title_length] + "..."
    return content
