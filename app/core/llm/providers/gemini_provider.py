"""
Google Gemini provider implementation for LLM service
"""

import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from app.core.llm.interface import LLMProvider
from app.core.config import Settings

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Provider for Google Gemini API"""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize Gemini provider with settings"""
        self.settings = settings or Settings()
        self.api_key = self.settings.gemini_api_key
        
        # Initialize Google AI client with API key
        self.client = genai.Client(api_key=self.api_key)
        
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a completion from Google Gemini"""
        model_name = model or self.settings.default_model
        temp_value = temperature or self.settings.default_temperature
        max_tokens_value = max_tokens or self.settings.max_tokens
        
        logger.info(f"Sending request to Google Gemini API with model: {model_name}")
        
        try:
            # Convert OpenAI format messages to Gemini format
            gemini_contents = []
            system_content = None
            
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    system_content = content
                    continue
                
                gemini_role = "user" if role == "user" else "model"
                gemini_contents.append({"role": gemini_role, "parts": [content]})
            
            # Configure generation parameters
            generation_config = types.GenerateContentConfig(
                temperature=temp_value,
                max_output_tokens=max_tokens_value,
                system_instruction=system_content
            )
            
            # Convert messages to proper Content objects
            contents = []
            for msg in gemini_contents:
                if msg["role"] == "user":
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=msg["parts"][0])]
                    ))
                else:
                    contents.append(types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=msg["parts"][0])]
                    ))
            
            # Make the API call - works for both single message and chat history
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config=generation_config
            )
            
            return {
                "message": {
                    "role": "assistant",
                    "content": response.text,
                },
                "usage": {},  # Gemini doesn't provide detailed token usage
            }
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error generating Gemini response: {error_message}")
            logger.exception("Full exception details:")
            
            # Handle rate limit errors
            if any(term in error_message.lower() for term in ["rate limit", "quota", "429"]):
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
                    "content": "I'm sorry, but there was an error with the AI service. Please try again later.",
                },
                "error": "api_error"
            }