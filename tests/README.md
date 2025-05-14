# End-to-End Tests for Ikkyu-san AI Chatbot

This directory contains end-to-end tests for the Ikkyu-san AI Chatbot application, focusing on the Gemini API provider with the Gemini Pro model.

## Test Structure

The tests are organized into two main classes:

- `TestGeminiProviderE2E` - Tests for direct interaction with the Gemini provider
- `TestChatEndpointE2E` - Tests for the chat API endpoint

## Test Philosophy

These tests are designed to verify that:

1. The application can connect to the Gemini API successfully
2. The Gemini Pro model can process and respond to various prompts
3. System prompts properly influence the model's responses
4. The model can handle multi-turn conversations
5. The API endpoints function correctly with the Gemini provider

## Running Tests

### Prerequisites

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Setting Up API Key

Most tests require a valid Gemini API key. You can set it as an environment variable:

```bash
# On Windows
set GEMINI_API_KEY=your_api_key_here

# On Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

### Running All Tests

```bash
pytest
```

### Running Specific Tests

```bash
# Run just the Gemini provider tests
pytest tests/e2e_tests.py::TestGeminiProviderE2E

# Run just the chat endpoint tests
pytest tests/e2e_tests.py::TestChatEndpointE2E

# Run a specific test
pytest tests/e2e_tests.py::TestGeminiProviderE2E::test_factual_knowledge
```

## Test Output

The tests will output detailed logs showing:

1. Connection status to the Gemini API
2. Request content sent to the API
3. Response content received from the API
4. Test assertions and results

If the API connection fails, most tests will be skipped with a notification 