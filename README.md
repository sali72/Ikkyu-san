# Ikkyu-san AI Chatbot Backend

A FastAPI-based AI chatbot backend that integrates with LLM providers like OpenRouter and Google Gemini.

## Features

- FastAPI backend with async support
- Integration with OpenRouter API and Google Gemini (supports multiple LLM providers)
- Conversation context management with MongoDB
- Token-based windowing system for managing context length
- Configurable system prompts, temperature, and model selection
- Clean, modular architecture for easy expansion

## Project Structure

```
app/
├── api/               # API routes and endpoints
├── core/              # Core business logic
│   ├── llm/           # LLM service implementation
│   │   └── providers/ # LLM provider implementations
├── crud/              # Database operations
├── schemas/           # Data validation schemas
└── models.py          # Database models
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start MongoDB:
   - Install MongoDB locally or use MongoDB Atlas
   - Update the connection string in `.env` file

5. Create a `.env` file with your API keys and settings:
   ```
   # API Keys
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here

   # LLM Configuration
   LLM_PROVIDER=gemini  # Options: openrouter, gemini
   DEFAULT_MODEL=gemini-2.0-flash
   DEFAULT_TEMPERATURE=0.7
   MAX_TOKENS=1000
   SYSTEM_PROMPT="You are a helpful AI assistant."
   
   # Context Configuration
   CONTEXT_WINDOW_SIZE=10
   
   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=ikkyu_san_chatbot
   ```

> **Important**: You must use valid API keys. Sign up at [OpenRouter](https://openrouter.ai) or [Google AI Studio](https://ai.google.dev/) to get your API keys.

## Usage

Start the development server:

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

- `GET /` - Root endpoint (status check)
- `POST /api/chat` - Chat with the LLM with conversation context
- `GET /api/conversations` - List user conversations
- `GET /api/conversations/{conversation_id}` - Get messages for a specific conversation
- `DELETE /api/conversations/{conversation_id}` - Delete a conversation

### Chat Request Example

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "model": "gemini-2.0-flash",
  "temperature": 0.7,
  "max_tokens": 1000,
  "system_prompt": "You are a helpful AI assistant.",
  "user_id": "user-123",
  "conversation_id": null
}
```

For new conversations, set `conversation_id` to `null` or omit it. To continue an existing conversation, provide the conversation ID returned in the previous response.

### Response Example

```json
{
  "message": {
    "role": "assistant",
    "content": "I'm doing well, thank you for asking! How can I assist you today?"
  },
  "usage": {},
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Conversation Context Management

The chatbot maintains conversation context by:

1. Storing all messages in a MongoDB database using Beanie ODM
2. Using a sliding window approach to include only the most recent N messages (configurable via `CONTEXT_WINDOW_SIZE`)
3. Automatically creating new conversations or continuing existing ones
4. Tracking token usage for each conversation

This implementation allows the chatbot to maintain context across multiple interactions while keeping the context window manageable.

## Future Enhancements

- Authentication and user management
- Rate limiting and usage tracking
- Fine-tuning support
- Streaming responses
- Multi-modal support

## Troubleshooting

### Invalid or malformed responses

If you receive responses that contain unusual text like `#<jupyter_text>` or regex information:

1. Verify your API key is valid and has sufficient credits
2. Try another model by setting `DEFAULT_MODEL` in your .env file to a different model like:
   - `anthropic/claude-3-opus:beta`
   - `meta-llama/llama-3-70b-instruct`
   - `google/gemini-pro`

3. Run the test script to debug:
   ```
   python test_api.py
   ```

4. Check your logs for more detailed information

### MongoDB Connection Issues

If you encounter MongoDB connection issues:

1. Verify MongoDB is running and accessible
2. Check the connection string in your `.env` file
3. Make sure network permissions allow connections to MongoDB
4. Check MongoDB logs for any authentication errors
