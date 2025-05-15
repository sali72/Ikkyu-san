"""
OpenRouter provider implementation for LLM service
"""

import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.core.llm.interface import LLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterProvider(LLMProvider):
    """Provider for OpenRouter API"""
    
    def __init__(self):
        """Initialize OpenRouter provider"""
        self.api_key = settings.openrouter_api_key
        
        # Initialize OpenAI client with OpenRouter base URL
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://ikkyu-san-chatbot.example.com",  # Update in production
                "X-Title": "Ikkyu-san AI Chatbot",  # Identify your application to OpenRouter
            }
        )
        
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a completion from OpenRouter"""
        model_name = model or settings.default_model
        temp_value = temperature or settings.default_temperature
        max_tokens_value = max_tokens or settings.max_tokens
        
        logger.info(f"Sending request to OpenRouter API with model: {model_name}")
        
        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temp_value,
                max_tokens=max_tokens_value,
                **kwargs
            )
            
            logger.debug(f"OpenRouter API response: {response}")
            
            # Check for error field in response
            if hasattr(response, 'error') and response.error:
                error_info = response.error
                error_message = error_info.get('message', 'Unknown API error')
                error_code = error_info.get('code', 0)
                
                # Handle rate limit errors
                if error_code == 429:
                    return {
                        "message": {
                            "role": "assistant",
                            "content": f"Rate limit exceeded. {error_message}",
                        },
                        "error": "rate_limit"
                    }
                
                # Handle other API errors
                return {
                    "message": {
                        "role": "assistant",
                        "content": f"API error: {error_message}",
                    },
                    "error": "api_error"
                }
            
            # Check if choices is None or empty
            if not response.choices:
                logger.error(f"No choices in response: {response}")
                return {
                    "message": {
                        "role": "assistant",
                        "content": "No response received from the API.",
                    },
                    "error": "no_response"
                }
            
            # Extract the assistant message and usage information
            assistant_message = response.choices[0].message
            usage = response.usage.model_dump() if response.usage else {}
            
            # Clean up response content if needed
            content = assistant_message.content or ""
            if content.startswith("#<jupyter_text>"):
                content = content.replace("#<jupyter_text>", "").strip()
            
            return {
                "message": {
                    "role": assistant_message.role,
                    "content": content,
                },
                "usage": usage,
            }
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error generating OpenRouter response: {error_message}")
            
            # Handle rate limit errors
            if "rate limit" in error_message.lower() or "429" in error_message:
                return {
                    "message": {
                        "role": "assistant",
                        "content": "Rate limit exceeded. Please try again later.",
                    },
                    "error": "rate_limit"
                }
            
            # Return a user-friendly error message
            return {
                "message": {
                    "role": "assistant",
                    "content": f"Error: {error_message}",
                },
                "error": "api_error"
            }