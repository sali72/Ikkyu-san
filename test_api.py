"""
Test script for the Ikkyu-san AI Chatbot API
"""
import asyncio
import json
import sys
import os
import logging

import aiohttp
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

API_BASE_URL = "http://127.0.0.1:8000"

async def test_chat_api():
    """Test the chat API endpoint"""
    chat_endpoint = f"{API_BASE_URL}/api/chat"
    
    # Test message
    request_data = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you introduce yourself?"
            }
        ],
        "model": "openai/gpt-3.5-turbo",  # Specify a well-known model
        "temperature": 0.7,
        "max_tokens": 200  # Keep it short for testing
    }
    
    logger.info(f"Sending request to {chat_endpoint}")
    logger.info(f"Request data: {json.dumps(request_data, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(chat_endpoint, json=request_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API error: {response.status}, {error_text}")
                    return False
                
                result = await response.json()
                logger.info("Response received:")
                logger.info(f"Status: {response.status}")
                logger.info(f"Response: {json.dumps(result, indent=2)}")
                
                return True
    except Exception as e:
        logger.error(f"Error testing API: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting API test")
    success = asyncio.run(test_chat_api())
    if success:
        logger.info("API test completed successfully")
        sys.exit(0)
    else:
        logger.error("API test failed")
        sys.exit(1) 