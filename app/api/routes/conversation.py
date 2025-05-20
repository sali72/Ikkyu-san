"""
Conversation management API routes
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query, Path

from app.schemas.chat import ConversationList, ConversationInfo
from app.services import conversation as conversation_service

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


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

        # Format the response
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

        # Get total count
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
    "/conversations/{conversation_id}/messages",
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

    return {"messages": conversation.messages}
