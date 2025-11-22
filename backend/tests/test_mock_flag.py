import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Test 1: Check environment variable
print("=" * 50)
print("TEST 1: Environment Variable Check")
print("=" * 50)
mock_flag = os.getenv("USE_MOCK_LLM", "false")
print(f"USE_MOCK_LLM raw value: '{mock_flag}'")
print(f"USE_MOCK_LLM.lower(): '{mock_flag.lower()}'")
print(f"Comparison result: {mock_flag.lower() == 'true'}")
print()

# Test 2: Import and test the LLM client
print("=" * 50)
print("TEST 2: LLM Client Mock Response")
print("=" * 50)
import asyncio
from backend.orchestrator.llm_client import generate_response

async def test_mock():
    response = await generate_response("Test prompt")
    print(f"Response intent: {response.get('intent')}")
    print(f"Response text: {response.get('reply_text')}")
    print(f"Is mock response: {response.get('intent') == 'mock_greeting'}")
    return response

result = asyncio.run(test_mock())
print()
print("=" * 50)
print("RESULT:")
print("=" * 50)
if result.get('intent') == 'mock_greeting':
    print("✅ MOCK LLM IS WORKING!")
else:
    print("❌ MOCK LLM NOT WORKING - Using real Gemini or fallback")
    print(f"Full response: {result}")
