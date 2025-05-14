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


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint
    """

    message: Message = Field(..., description="The assistant's response message")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage information")
