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
            # Process messages and prepare for LLM
            processed_messages = self._prepare_messages(messages, system_prompt)

            # Get response from provider
            response = await self._get_provider_response(
                processed_messages, model, temperature, max_tokens
            )

            return response

        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            logger.exception("Full exception details:")
            return self._create_error_response("service_error")

    def _prepare_messages(
        self,
        messages: List[Union[Message, Dict[str, str]]],
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Prepare messages for the LLM provider

        Args:
            messages: List of messages to process
            system_prompt: Optional system prompt to include

        Returns:
            List of processed messages in dict format
        """
        processed_messages = []

        # Add system prompt if provided
        if system_prompt:
            processed_messages.append({"role": "system", "content": system_prompt})

        # Process and add all messages
        for message in messages:
            if isinstance(message, dict):
                processed_messages.append(message)
            else:
                processed_messages.append(
                    {"role": message.role, "content": message.content}
                )

        return processed_messages

    async def _get_provider_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get response from the LLM provider

        Args:
            messages: Processed messages to send to the provider
            model: LLM model to use
            temperature: Temperature setting
            max_tokens: Maximum tokens for response

        Returns:
            Response from the provider with standardized format
        """
        # Delegate to the provider
        response = await self.provider.generate_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Ensure response has a "usage" field
        if "usage" not in response:
            response["usage"] = None

        return response

    def _create_error_response(self, error_type: str) -> Dict[str, Any]:
        """
        Create a standardized error response

        Args:
            error_type: Type of error that occurred

        Returns:
            Error response in standard format
        """
        return {
            "message": {
                "role": "assistant",
                "content": "I'm sorry, but there was an error processing your request. Please try again later.",
            },
            "usage": None,
            "error": error_type,
        }
