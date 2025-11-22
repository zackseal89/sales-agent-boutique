import os
import sys
import json
import asyncio
import unittest
from unittest import mock

# Ensure the backend package is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.orchestrator.llm_client import generate_response

class TestLLMClient(unittest.IsolatedAsyncioTestCase):
    async def test_mock_flag_enabled(self):
        # Enable mock flag
        os.environ['USE_MOCK_LLM'] = 'true'
        response = await generate_response('any prompt')
        self.assertEqual(response['intent'], 'mock_greeting')
        self.assertIn('mock Gemini response', response['reply_text'])
        # Clean up
        del os.environ['USE_MOCK_LLM']

    @mock.patch('backend.orchestrator.llm_client.genai')
    async def test_real_call_returns_parsed_json(self, mock_genai):
        # Disable mock flag
        os.environ['USE_MOCK_LLM'] = 'false'
        # Mock Gemini model and response
        mock_model = mock.Mock()
        mock_response = mock.Mock()
        mock_response.text = json.dumps({
            "reply_text": "Real response",
            "actions": [],
            "intent": "greeting",
            "entities": {}
        })
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.GenerationConfig.return_value = None
        # Call generate_response
        result = await generate_response('test prompt')
        self.assertEqual(result['reply_text'], 'Real response')
        self.assertEqual(result['intent'], 'greeting')
        # Clean up
        del os.environ['USE_MOCK_LLM']

if __name__ == '__main__':
    asyncio.run(unittest.main())
