#!/usr/bin/env python
"""
Script to list available models in Google Generative AI
"""

import os
import sys
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Get the API key from environment
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable not set")
    sys.exit(1)

# Initialize the client
client = genai.Client(api_key=api_key)

# List available models
print("Available models:")
try:
    models = client.models.list()
    for model in models:
        print(f"- {model.name}")
        # Print additional details if available
        if hasattr(model, "description") and model.description:
            print(f"  Description: {model.description}")
        if hasattr(model, "supported_generation_methods"):
            print(f"  Supported methods: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"Error listing models: {str(e)}")
    print(f"Exception type: {type(e)}")
    sys.exit(1) 