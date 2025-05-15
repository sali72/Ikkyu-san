"""
LLM service integration for chat functionality with multiple providers
"""

import logging
from typing import List, Dict, Any, Optional, Union
from app.core.config import settings
from app.schemas.chat import Message
from app.core.llm.factory import create_llm_provider

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with various LLM providers"""

    def __init__(self):
        """Initialize LLM service"""
        self.provider = create_llm_provider(settings.llm_provider)

    async def generate_response(
        self,
        messages: List[Union[Message, Dict[str, str]]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM based on conversation history

        Args:
            messages: List of conversation messages (can be Message objects or dicts)
            model: LLM model to use
            temperature: Temperature setting for response randomness
            max_tokens: Maximum tokens in the response
            system_prompt: System prompt to guide the model

        Returns:
            Dictionary with the LLM response and usage information
        """
        try:
            # Prepare the system message if provided
            processed_messages = []
            if system_prompt:
                processed_messages.append({"role": "system", "content": system_prompt})

            # Add user messages
            for message in messages:
                if isinstance(message, dict):
                    # Message is already a dict, just add it to processed_messages
                    processed_messages.append(message)
                else:
                    # Message is a Message object, convert to dict
                    processed_messages.append(
                        {"role": message.role, "content": message.content}
                    )
            
            # Delegate to the provider
            response = await self.provider.generate_completion(
                messages=processed_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Ensure response has a "usage" field
            if "usage" not in response:
                response["usage"] = None
            
            return response

        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            logger.exception("Full exception details:")
            
            # Return a user-friendly error message instead of raising
            return {
                "message": {
                    "role": "assistant",
                    "content": "I'm sorry, but there was an error processing your request. Please try again later.",
                },
                "usage": None,  # Ensure usage field is always present
                "error": "service_error",
            }
