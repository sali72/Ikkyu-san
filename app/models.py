"""
Beanie ODM models for conversation context
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field
from beanie import Document, Indexed
from typing import Annotated
from app.schemas.chat import Message


class Conversation(Document):
    """
    Document model for storing conversation context
    """

    user_id: Annotated[str, Indexed()] = Field(
        ..., description="Unique identifier for the user"
    )
    conversation_id: Annotated[str, Indexed()] = Field(
        ..., description="Unique identifier for the conversation"
    )
    title: Optional[str] = Field(None, description="Title of the conversation")
    messages: List[Message] = Field(
        default_factory=list, description="Messages in the conversation"
    )
    model: Optional[str] = Field(None, description="LLM model used in the conversation")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    token_count: int = Field(
        default=0, description="Total token count in the conversation"
    )

    class Settings:
        name = "conversations"
        indexes = [
            "user_id",
            "conversation_id",
            ("user_id", "conversation_id"),  # Compound index
        ]
