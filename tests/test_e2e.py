"""
End-to-end tests for the AI chatbot application
"""

import pytest
from fastapi import status


@pytest.mark.e2e
class TestChatEndpointE2E:
    """
    End-to-end tests for the chat endpoint
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
                "max_tokens": 50,
                "user_id": "test-user-123",
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
                "max_tokens": 100,
                "system_prompt": "You are a comedian AI that tells jokes.",
                "user_id": "test-user-123",
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
