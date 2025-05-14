"""
Google Gemini provider implementation for LLM service
"""

import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.core.llm_service.interface import LLMProvider
from app.core.config import Settings

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Provider for Google Gemini API"""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Initialize Gemini provider with settings"""
        self.settings = settings or Settings()
        self.api_key = self.settings.gemini_api_key
        
        # Initialize Google AI client with API key
        genai.configure(api_key=self.api_key)
        
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
            gemini_messages = []
            system_content = None
            
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    system_content = content
                    continue
                
                gemini_role = "user" if role == "user" else "model"
                gemini_messages.append({"role": gemini_role, "parts": [content]})
            
            # Initialize the model with system prompt if available
            generation_config = {
                "temperature": temp_value,
                "max_output_tokens": max_tokens_value,
            }
            
            gemini_model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_content
            )
            
            # For simple completion without chat history
            if len(gemini_messages) == 1:
                response = gemini_model.generate_content(gemini_messages[0]["parts"][0])
                return {
                    "message": {
                        "role": "assistant",
                        "content": response.text,
                    },
                    "usage": {},  # Gemini doesn't provide detailed token usage
                }
            
            # For chat with history
            chat_session = gemini_model.start_chat(history=[])
            
            # Add all messages except the last one to history
            for i in range(len(gemini_messages) - 1):
                msg = gemini_messages[i]
                if msg["role"] == "user":
                    chat_session.send_message(msg["parts"][0])
                
            # Send the last message and get response
            last_message = gemini_messages[-1]["parts"][0]
            response = chat_session.send_message(last_message)
            
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