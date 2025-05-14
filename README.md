# Ikkyu-san AI Chatbot Backend

A FastAPI-based AI chatbot backend that integrates with LLM providers like OpenRouter.

## Features

- FastAPI backend with async support
- Integration with OpenRouter API (supports multiple LLM providers)
- Configurable system prompts, temperature, and model selection
- Clean, modular architecture for easy expansion

## Project Structure

```
app/
├── api/               # API routes and endpoints
├── config/            # Configuration settings
├── core/              # Core business logic
└── schemas/           # Data validation schemas
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
4. Create a `.env` file with your OpenRouter API key:
   ```
   # API Keys
   OPENROUTER_API_KEY=your_openrouter_api_key_here

   # LLM Configuration
   DEFAULT_MODEL=openai/gpt-3.5-turbo
   DEFAULT_TEMPERATURE=0.7
   MAX_TOKENS=1000
   SYSTEM_PROMPT="You are a helpful AI assistant."
   ```

> **Important**: You must use a valid OpenRouter API key. Sign up at [OpenRouter](https://openrouter.ai) to get your API key.

## Usage

Start the development server:

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

- `GET /` - Root endpoint (status check)
- `POST /api/chat` - Chat with the LLM

### Chat Request Example

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "model": "openai/gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 1000,
  "system_prompt": "You are a helpful AI assistant."
}
```

## Future Enhancements

- Message history storage
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
