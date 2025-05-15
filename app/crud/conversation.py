"""
Service for managing conversation context
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.schemas.chat import Message
from app.models import Conversation

logger = logging.getLogger(__name__)


async def get_conversation(
    user_id: str, conversation_id: str
) -> Optional[Conversation]:
    """
    Retrieve a conversation by user_id and conversation_id

    Args:
        user_id: Unique identifier for the user
        conversation_id: Unique identifier for the conversation

    Returns:
        The conversation document or None if not found
    """
    return await Conversation.find_one(
        {"user_id": user_id, "conversation_id": conversation_id}
    )


async def create_conversation(
    user_id: str, title: Optional[str] = None, model: Optional[str] = None
) -> Conversation:
    """
    Create a new conversation

    Args:
        user_id: Unique identifier for the user
        title: Optional title for the conversation
        model: Optional model used for the conversation

    Returns:
        The new conversation document
    """
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(
        user_id=user_id,
        conversation_id=conversation_id,
        title=title,
        model=model,
        messages=[],
        token_count=0,
    )
    return await conversation.insert()


async def add_message(
    user_id: str, conversation_id: str, message: Message, token_count: int = 0
) -> Conversation:
    """
    Add a message to a conversation

    Args:
        user_id: Unique identifier for the user
        conversation_id: Unique identifier for the conversation
        message: Message to add to the conversation
        token_count: Token count of the message

    Returns:
        Updated conversation document
    """
    conversation = await get_conversation(user_id, conversation_id)

    if not conversation:
        logger.warning(
            f"Conversation {conversation_id} not found for user {user_id}, creating new one"
        )
        conversation = await create_conversation(user_id, model=settings.default_model)

    # Add message to conversation
    conversation.messages.append(message)
    conversation.token_count += token_count
    conversation.updated_at = datetime.utcnow()

    # Update title if this is the first user message
    if (
        len(conversation.messages) == 1
        and message.role == "user"
        and not conversation.title
    ):
        # Use the first ~30 chars of the first message as the title
        conversation.title = (
            (message.content[:30] + "...")
            if len(message.content) > 30
            else message.content
        )

    await conversation.save()
    return conversation


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
    # Create a new list with system message if provided
    context = []
    if system_prompt:
        context.append({"role": "system", "content": system_prompt})

    # Take the last N messages based on context window size
    recent_messages = (
        messages[-settings.context_window_size :]
        if len(messages) > settings.context_window_size
        else messages
    )

    # Add recent messages to context
    for message in recent_messages:
        context.append({"role": message.role, "content": message.content})

    return context


async def list_conversations(
    user_id: str, limit: int = 10, skip: int = 0
) -> List[Conversation]:
    """
    List conversations for a user

    Args:
        user_id: Unique identifier for the user
        limit: Maximum number of conversations to return
        skip: Number of conversations to skip

    Returns:
        List of conversation documents
    """
    return (
        await Conversation.find({"user_id": user_id})
        .sort("-updated_at")
        .limit(limit)
        .skip(skip)
        .to_list()
    )


async def delete_conversation(user_id: str, conversation_id: str) -> bool:
    """
    Delete a conversation

    Args:
        user_id: Unique identifier for the user
        conversation_id: Unique identifier for the conversation

    Returns:
        True if the conversation was deleted, False otherwise
    """
    conversation = await get_conversation(user_id, conversation_id)
    if not conversation:
        return False

    await conversation.delete()
    return True
