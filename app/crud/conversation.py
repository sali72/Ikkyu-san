"""CRUD operations for conversation data"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional

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
    conversation_id = _generate_conversation_id()
    conversation = _create_conversation_object(user_id, conversation_id, title, model)
    return await conversation.insert()


def _generate_conversation_id() -> str:
    """Generate a unique conversation ID"""
    return str(uuid.uuid4())


def _create_conversation_object(
    user_id: str, 
    conversation_id: str, 
    title: Optional[str] = None, 
    model: Optional[str] = None
) -> Conversation:
    """Create a new conversation object"""
    return Conversation(
        user_id=user_id,
        conversation_id=conversation_id,
        title=title,
        model=model,
        messages=[],
        token_count=0,
    )


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
    # Get the conversation
    conversation = await get_conversation(user_id, conversation_id)
    
    if not conversation:
        logger.warning(f"Conversation {conversation_id} not found, creating new one")
        conversation = await create_conversation(user_id)
        
    # Add message to conversation
    conversation.messages.append(message)
    conversation.token_count += token_count
    conversation.updated_at = datetime.utcnow()

    # Update title if this is the first user message and no title exists
    if len(conversation.messages) == 1 and message.role == "user" and not conversation.title:
        # Use the first ~30 chars of the first message as the title
        max_length = 30
        conversation.title = (
            (message.content[:max_length] + "...")
            if len(message.content) > max_length
            else message.content
        )
    
    # Save the updated conversation
    await conversation.save()
    return conversation








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
    return await _query_conversations(user_id, limit, skip)


async def _query_conversations(user_id: str, limit: int, skip: int) -> List[Conversation]:
    """Query the database for conversations"""
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
