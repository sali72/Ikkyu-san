"""
LLM service integration for chat functionality
"""

import logging
from typing import List, Dict, Any, Optional
import aiohttp
from app.core.config import Settings
from app.schemas.chat import Message

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenRouter LLM API"""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize LLM service with settings"""
        self.settings = settings or Settings()
        self.api_key = self.settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ikkyu-san-chatbot.example.com",  # Update in production
            "X-Title": "Ikkyu-san AI Chatbot",  # Identify your application to OpenRouter
        }

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
        # Prepare the system message if provided
        processed_messages = []
        if system_prompt:
            processed_messages.append({"role": "system", "content": system_prompt})

        # Add user messages
        for message in messages:
            processed_messages.append(
                {"role": message.role, "content": message.content}
            )

        # Prepare the request payload
        payload = {
            "messages": processed_messages,
            "model": model or self.settings.default_model,
            "temperature": temperature or self.settings.default_temperature,
            "stream": False,
            "stop": None,
        }

        # Add max_tokens if specified
        if max_tokens or self.settings.max_tokens:
            payload["max_tokens"] = max_tokens or self.settings.max_tokens

        logger.info(f"Sending request to OpenRouter API with model: {payload['model']}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30,  # Set timeout to 30 seconds
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"LLM API error: {response.status}, {error_text}")
                        raise Exception(
                            f"LLM API error: {response.status}, details: {error_text}"
                        )

                    response_json = await response.json()
                    logger.debug(f"OpenRouter API response: {response_json}")

                    # Extract the assistant message and usage information
                    assistant_message = response_json.get("choices", [{}])[0].get(
                        "message", {}
                    )
                    usage = response_json.get("usage", {})

                    # Clean up response content if needed
                    content = assistant_message.get("content", "")
                    if content.startswith("#<jupyter_text>"):
                        content = content.replace("#<jupyter_text>", "").strip()

                    return {
                        "message": {
                            "role": assistant_message.get("role", "assistant"),
                            "content": content,
                        },
                        "usage": usage,
                    }
        except aiohttp.ClientError as e:
            logger.error(f"Network error communicating with OpenRouter API: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
