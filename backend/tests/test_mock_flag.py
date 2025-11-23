import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.orchestrator.llm_client import generate_response

@pytest.mark.anyio
async def test_mock():
    """
    Tests that the LLM client returns a mock response when USE_MOCK_LLM is true.
    """
    # Set the environment variable to ensure the mock is used
    os.environ['USE_MOCK_LLM'] = 'true'

    response = await generate_response("Test prompt")

    assert response.get('intent') == 'mock_greeting', "The intent should be 'mock_greeting'"
    assert "Hello! I'm a mock Gemini response." in response.get('reply_text', ''), "The reply text should contain the mock response message"
