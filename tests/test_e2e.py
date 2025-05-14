"""
End-to-end tests for the AI chatbot application with Gemini provider
"""

import pytest
from fastapi import status


@pytest.mark.e2e
class TestGeminiProviderE2E:
    """
    End-to-end tests for the Gemini provider
    """

    @pytest.mark.api
    def test_api_connection(self, check_gemini_connection):
        """Test if we can connect to the Gemini API"""
        is_connected, message = check_gemini_connection

        # If API connection fails, mark this test as failed and skip other API tests
        if not is_connected:
            pytest.skip(f"Skipping all API tests: {message}")
        
        
        
        assert is_connected, message

    
    async def test_basic_chat_response(self, gemini_provider):
        """Test basic chat functionality with a simple prompt"""
        messages = [{"role": "user", "content": "Hello, can you introduce yourself?"}]

        response = await gemini_provider.generate_completion(
            messages=messages, model="gemini-2.0-flash", temperature=0.7, max_tokens=200
        )

        # Basic validation
        assert "message" in response
        assert "role" in response["message"]
        assert "content" in response["message"]
        assert response["message"]["role"] == "assistant"
        assert len(response["message"]["content"]) > 0

        # Content should mention being an AI assistant
        content = response["message"]["content"].lower()
        assert any(term in content for term in ["ai", "assistant", "help", "bot"])

        # No error messages
        error_phrases = [
            "sorry",
            "error",
            "couldn't process",
            "rate limit",
            "don't know",
        ]
        assert not any(phrase in content for phrase in error_phrases)

    
    async def test_system_prompt_influence(self, gemini_provider):
        """Test that system prompts properly influence responses"""
        system_message = (
            "You are a pirate AI assistant who always speaks in pirate slang."
        )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": "Tell me about yourself."},
        ]

        response = await gemini_provider.generate_completion(
            messages=messages, model="gemini-2.0-flash", temperature=0.7, max_tokens=200
        )

        # Check for pirate slang in the response
        content = response["message"]["content"].lower()
        pirate_terms = [
            "arr",
            "matey",
            "ahoy",
            "ye",
            "treasure",
            "ship",
            "captain",
            "sea",
        ]

        # At least some pirate terms should be present if system prompt worked
        assert any(
            term in content for term in pirate_terms
        ), f"System prompt didn't influence response: {content}"

    
    async def test_factual_knowledge(self, gemini_provider):
        """Test factual knowledge of the model"""
        messages = [{"role": "user", "content": "What is the capital of France?"}]

        response = await gemini_provider.generate_completion(
            messages=messages,
            model="gemini-2.0-flash",
            temperature=0.2,  # Lower temp for factual responses
            max_tokens=100,
        )

        # Response should contain "Paris"
        content = response["message"]["content"].lower()
        assert (
            "paris" in content
        ), f"Model did not provide the correct capital: {content}"

    
    async def test_multi_turn_conversation(self, gemini_provider):
        """Test multi-turn conversation abilities"""
        # First message
        messages = [
            {"role": "user", "content": "My name is Alex and I like machine learning."}
        ]

        response1 = await gemini_provider.generate_completion(
            messages=messages, model="gemini-2.0-flash", max_tokens=150
        )

        # Add assistant response to the conversation
        messages.append(
            {"role": "assistant", "content": response1["message"]["content"]}
        )

        # Add follow-up question
        messages.append(
            {"role": "user", "content": "What was my name again and what do I like?"}
        )

        # Get second response
        response2 = await gemini_provider.generate_completion(
            messages=messages, model="gemini-2.0-flash", max_tokens=150
        )

        # Model should remember the name and interest
        content = response2["message"]["content"].lower()
        assert "alex" in content, "Model failed to remember the name"
        assert "machine learning" in content, "Model failed to remember the interest"


@pytest.mark.e2e
class TestChatEndpointE2E:
    """
    End-to-end tests for the chat endpoint with the Gemini provider
    """

    @pytest.mark.api
    def test_chat_endpoint_basic(self, test_client):
        """Test basic chat endpoint functionality"""
        # Simple request to the chat endpoint
        response = test_client.post(
            "/api/chat",
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, please give a very short greeting.",
                    }
                ],
                "model": "gemini-2.0-flash",
                "max_tokens": 50,
            },
        )

        # Validate response status and structure
        assert (
            response.status_code == status.HTTP_200_OK
        ), f"Request failed with status {response.status_code}: {response.text}"

        data = response.json()
        assert "message" in data
        assert "role" in data["message"]
        assert "content" in data["message"]
        assert data["message"]["role"] == "assistant"
        assert len(data["message"]["content"]) > 0

    @pytest.mark.api
    def test_chat_with_system_prompt(self, test_client):
        """Test chat endpoint with a custom system prompt"""
        # Request with a custom system prompt
        response = test_client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "Tell me a very short joke."}],
                "model": "gemini-2.0-flash",
                "max_tokens": 100,
                "system_prompt": "You are a comedian AI that tells jokes.",
            },
        )

        # Validate response
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        content = data["message"]["content"].lower()

        # Content should be humorous in some way
        humor_indicators = ["joke", "laugh", "funny", "?", "!"]
        assert any(
            indicator in content for indicator in humor_indicators
        ), f"Response doesn't seem to be a joke: {content}"
