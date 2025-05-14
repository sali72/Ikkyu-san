"""
LLM service integration for chat functionality with multiple providers
"""

import logging
from typing import List, Dict, Any, Optional
from app.core.config import Settings
from app.schemas.chat import Message
from app.core.llm.factory import create_llm_provider

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with various LLM providers"""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize LLM service with settings"""
        self.settings = settings or Settings()
        self.provider = create_llm_provider(self.settings.llm_provider, self.settings)

    async def generate_response(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM based on conversation history

        Args:
            messages: List of conversation messages
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
                processed_messages.append(
                    {"role": message.role, "content": message.content}
                )

            # Delegate to the provider
            return await self.provider.generate_completion(
                messages=processed_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            logger.exception("Full exception details:")
            
            # Return a user-friendly error message instead of raising
            return {
                "message": {
                    "role": "assistant",
                    "content": "I'm sorry, but there was an error processing your request. Please try again later.",
                },
                "error": "service_error",
            }
