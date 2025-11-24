"""
AI Model Utility
Provides a wrapper for calling the generative AI model (e.g., Google Gemini).
Includes a mock for development to avoid actual API calls.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the generative AI client
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    genai.configure(api_key=google_api_key)

# Environment variable to control mocking
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "false").lower() == "true"

async def call_ai_model(prompt: str) -> str:
    """
    Calls the configured AI model with the given prompt.
    Returns a mock response if USE_MOCK_LLM is set to true.
    """
    if USE_MOCK_LLM:
        print("🤖 Using mock AI model response.")
        return "This is a mock response from the AI model. The product is in stock."

    try:
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        model = genai.GenerativeModel('gemini-pro')
        response = await model.generate_content_async(prompt)

        # Accessing the text from the response parts
        if response.parts:
            return "".join(part.text for part in response.parts)
        # Fallback for simpler response structures
        elif hasattr(response, 'text'):
            return response.text
        else:
            # If the structure is different, you might need to inspect the response object
            # For debugging purposes:
            print(f"Unexpected AI response format: {response}")
            return "Error: Could not extract text from AI response."

    except Exception as e:
        print(f"Error calling AI model: {e}")
        # In case of an API error, you might want to return a fallback response
        # or re-raise the exception depending on your error handling strategy.
        return "Sorry, I am unable to process your request at the moment."
