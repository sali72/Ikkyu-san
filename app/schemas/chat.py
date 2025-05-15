"""
Schemas for chat requests and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    A single message in a chat conversation
    """

    role: str = Field(
        ..., description="Role of the message sender (user, assistant, system)"
    )
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint
    """

    messages: List[Message] = Field(
        ..., description="List of messages in the conversation"
    )
    model: Optional[str] = Field(None, description="LLM model to use for the response")
    temperature: Optional[float] = Field(
        None, description="Temperature for controlling response randomness"
    )
    max_tokens: Optional[int] = Field(
        None, description="Maximum number of tokens to generate"
    )
    system_prompt: Optional[str] = Field(
        None, description="System prompt to use for the conversation"
    )
    conversation_id: Optional[str] = Field(
        None, description="ID of the conversation to continue, or None for a new conversation"
    )
    user_id: str = Field(
        ..., description="Unique identifier for the user"
    )


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint
    """

    message: Message = Field(..., description="The assistant's response message")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")
    conversation_id: str = Field(..., description="ID of the conversation")


class ConversationInfo(BaseModel):
    """
    Basic information about a conversation
    """
    
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    title: Optional[str] = Field(None, description="Title of the conversation")
    updated_at: str = Field(..., description="Last update timestamp as ISO format string")
    model: Optional[str] = Field(None, description="LLM model used in the conversation")
    message_count: int = Field(..., description="Number of messages in the conversation")


class ConversationList(BaseModel):
    """
    List of conversations for a user
    """
    
    conversations: List[ConversationInfo] = Field(..., description="List of conversation information")
    total: int = Field(..., description="Total number of conversations for the user")
