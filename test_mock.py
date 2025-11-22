import os
import asyncio
import sys

# Set environment variable
os.environ['USE_MOCK_LLM'] = 'true'

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.orchestrator.llm_client import generate_response

async def main():
    print("Testing Mock LLM...")
    print(f"USE_MOCK_LLM = {os.getenv('USE_MOCK_LLM')}")
    print()
    
    result = await generate_response("Hello, test message")
    
    print("Response:")
    print(f"  Intent: {result.get('intent')}")
    print(f"  Reply: {result.get('reply_text')[:80]}...")
    print()
    
    if result.get('intent') == 'mock_greeting':
        print("✅ SUCCESS: Mock LLM is working!")
        return 0
    elif result.get('intent') == 'error':
        print("❌ FAIL: Got fallback error response")
        print(f"Full response: {result}")
        return 1
    else:
        print("⚠️  WARNING: Got unexpected response")
        print(f"Full response: {result}")
        return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
