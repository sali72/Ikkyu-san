"""
End-to-end tests for conversation management endpoints
"""

import pytest
import uuid
from fastapi import status


@pytest.mark.e2e
class TestConversationEndpointsE2E:
    """
    End-to-end tests for conversation management endpoints
    """
    # @pytest.fixture(scope="function", autouse=True)
    # async def clean_conversations_collection():
    #     client = await get_test_db_client()
    #     db = client[settings.mongodb_db_name]
    #     await db["conversations"].delete_many({})
    
    @pytest.fixture
    def test_user_id(self):
        """Generate a test user ID"""
        return f"test-user-{uuid.uuid4()}"
    
    @pytest.fixture
    def test_conversation(self, test_client, test_user_id):
        """Create a test conversation and return its ID"""
        # Create a conversation by sending a chat message
        response = test_client.post(
            "/api/chat",
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": "This is a test conversation for e2e testing.",
                    }
                ],
                "user_id": test_user_id,
            },
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Return both conversation ID and user ID for convenience
        return {
            "conversation_id": data["conversation_id"],
            "user_id": test_user_id
        }
    
    @pytest.mark.api
    def test_list_conversations_empty(self, test_client, test_user_id):
        """Test listing conversations when none exist for the user"""
        # List conversations for a new user (should be empty)
        response = test_client.get(
            f"/api/conversations?user_id={test_user_id}"
        )
        
        # Validate response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check structure and content
        assert "conversations" in data
        assert "total" in data
        assert isinstance(data["conversations"], list)
        assert data["total"] == 0
        assert len(data["conversations"]) == 0
    
    @pytest.mark.api
    def test_list_conversations_with_data(self, test_client, test_conversation):
        """Test listing conversations when at least one exists"""
        # List conversations for a user with a conversation
        response = test_client.get(
            f"/api/conversations?user_id={test_conversation['user_id']}"
        )
        
        # Validate response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check structure and content
        assert "conversations" in data
        assert "total" in data
        assert isinstance(data["conversations"], list)
        assert data["total"] >= 1
        assert len(data["conversations"]) >= 1
        
        # Verify conversation properties
        conversation = data["conversations"][0]
        assert "conversation_id" in conversation
        assert "title" in conversation
        assert "updated_at" in conversation
        assert "model" in conversation
        assert "message_count" in conversation
        assert conversation["message_count"] >= 1
    
    @pytest.mark.api
    def test_get_conversation_messages(self, test_client, test_conversation):
        """Test getting messages from a conversation"""
        # Get messages for the test conversation
        response = test_client.get(
            f"/api/conversations/{test_conversation['conversation_id']}/messages?user_id={test_conversation['user_id']}"
        )
        
        # Validate response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check structure and content
        assert "messages" in data
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) >= 1
        
        # Verify message properties
        message = data["messages"][0]
        assert "role" in message
        assert "content" in message
        assert message["role"] in ["user", "assistant", "system"]
        assert len(message["content"]) > 0
    
    @pytest.mark.api
    def test_get_nonexistent_conversation(self, test_client, test_user_id):
        """Test getting messages from a nonexistent conversation"""
        # Try to get messages for a nonexistent conversation
        fake_conversation_id = str(uuid.uuid4())
        response = test_client.get(
            f"/api/conversations/{fake_conversation_id}/messages?user_id={test_user_id}"
        )
        
        # Should return 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.api
    def test_delete_conversation(self, test_client, test_conversation):
        """Test deleting a conversation"""
        # Delete the test conversation
        response = test_client.delete(
            f"/api/conversations/{test_conversation['conversation_id']}?user_id={test_conversation['user_id']}"
        )
        
        # Should return 204 No Content
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the conversation was deleted by trying to get its messages
        verify_response = test_client.get(
            f"/api/conversations/{test_conversation['conversation_id']}/messages?user_id={test_conversation['user_id']}"
        )
        
        # Should return 404 Not Found
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.api
    def test_delete_nonexistent_conversation(self, test_client, test_user_id):
        """Test deleting a nonexistent conversation"""
        # Try to delete a nonexistent conversation
        fake_conversation_id = str(uuid.uuid4())
        response = test_client.delete(
            f"/api/conversations/{fake_conversation_id}?user_id={test_user_id}"
        )
        
        # Should return 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
