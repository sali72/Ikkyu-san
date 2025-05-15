"""
Google Gemini provider implementation for LLM service
"""

import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from app.core.llm.interface import LLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Provider for Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini provider"""
        self.api_key = settings.gemini_api_key
        
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
        model_name = model or settings.default_model
        temp_value = temperature or settings.default_temperature
        max_tokens_value = max_tokens or settings.max_tokens
        
        logger.info(f"Sending request to Google Gemini API with model: {model_name}")
        
        try:
            # Convert OpenAI format messages to Gemini format
            gemini_contents = []
            system_content = None
            
            # Extract the last user message for special handling
            last_user_message = None
            last_user_index = -1
            
            # Find the last user message in the conversation
            for i in range(len(messages) - 1, -1, -1):
                if messages[i]["role"] == "user":
                    last_user_message = messages[i]["content"]
                    last_user_index = i
                    break
            
            # Process all messages
            for i, msg in enumerate(messages):
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    # Enhance system message to emphasize responding to the latest message
                    if "focus on the most recent user message" not in content.lower():
                        system_content = (content + 
                            " Focus on the most recent user message and provide a direct response to it rather than continuing previous topics.")
                    else:
                        system_content = content
                    continue
                
                # Add emphasis to the last user message to ensure model pays attention to it
                if i == last_user_index and last_user_message:
                    content = f"Respond directly to this question/message: {content}"
                
                gemini_role = "user" if role == "user" else "model"
                gemini_contents.append({"role": gemini_role, "parts": [content]})
            
            # If no system content was provided, add one to focus on the latest message
            if not system_content:
                system_content = "You are a helpful AI assistant. Focus on the most recent user message and provide a direct response to it rather than continuing previous topics."
            
            # Configure generation parameters
            generation_config = types.GenerateContentConfig(
                temperature=temp_value,
                max_output_tokens=max_tokens_value,
                system_instruction=system_content
            )
            
            # Handle empty message list
            if not gemini_contents:
                # Add a default user message if no messages are provided
                gemini_contents.append({
                    "role": "user", 
                    "parts": ["Hello, I need some assistance."]
                })
            
            # Ensure conversations alternate between user and model
            # If the last message is from the model, add a placeholder user message
            if gemini_contents and gemini_contents[-1]["role"] == "model":
                gemini_contents.append({
                    "role": "user", 
                    "parts": ["Please continue."]
                })
            
            # Convert messages to proper Content objects
            contents = []
            for msg in gemini_contents:
                if msg["role"] == "user":
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=part) for part in msg["parts"]]
                    ))
                else:
                    contents.append(types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=part) for part in msg["parts"]]
                    ))
            
            # Ensure we have at least one content object for the API
            if not contents:
                # Add a default user message if conversion resulted in empty contents
                contents = [types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="Hello, I need some assistance.")]
                )]
            
            # Log the contents for debugging
            logger.debug(f"Sending contents to Gemini: {contents}")
            
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
                    "error": "rate_limit",
                    "usage": {}
                }
            
            # Return a user-friendly error message
            return {
                "message": {
                    "role": "assistant",
                    "content": "I'm sorry, but there was an error with the AI service. Please try again later.",
                },
                "error": "api_error",
                "usage": {}
            }