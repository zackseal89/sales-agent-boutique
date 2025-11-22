import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock services BEFORE importing orchestrator
sys.modules["services.supabase_service"] = MagicMock()
sys.modules["services.paylink_service"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

# Setup mocks
mock_supabase = sys.modules["services.supabase_service"].supabase_service
mock_paylink = sys.modules["services.paylink_service"].paylink_service
mock_genai = sys.modules["google.generativeai"]

# Mock Supabase client responses
mock_client = MagicMock()
mock_supabase.client = mock_client

# Mock conversation lookup
mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute = AsyncMock(return_value=MagicMock(data=[{"id": "test-conv-id", "metadata": {}}]))
mock_client.table.return_value.insert.return_value.execute = AsyncMock(return_value=MagicMock(data=[{"id": "test-conv-id"}]))

# Mock product lookup
mock_client.table.return_value.select.return_value.eq.return_value.gt.return_value.limit.return_value.execute = AsyncMock(return_value=MagicMock(data=[
    {"id": "prod-1", "name": "Blue Floral Dress", "price": 2500, "stock_quantity": 5, "sizes": ["S", "M", "L"], "colors": ["Blue"]}
]))

# Mock LLM response
mock_model = MagicMock()
mock_genai.GenerativeModel.return_value = mock_model
mock_response = MagicMock()
mock_response.text = '{"reply_text": "I found a Blue Floral Dress for KES 2,500. Would you like to buy it?", "actions": [{"tool": "search_products", "params": {"query": "dress"}}], "intent": "product_search"}'
mock_model.generate_content_async = AsyncMock(return_value=mock_response)

# Now import orchestrator
from orchestrator.message_handler import handle_whatsapp_message

async def test_orchestrator():
    print("🚀 Starting Orchestrator Test...")
    
    # Mock Request
    mock_request = MagicMock()
    mock_request.form = AsyncMock(return_value={
        "From": "whatsapp:+254712345678",
        "To": "whatsapp:+14155238886",
        "Body": "Do you have any dresses?",
        "MediaUrl0": None
    })
    
    print("📨 Sending message: 'Do you have any dresses?'")
    
    try:
        result = await handle_whatsapp_message(mock_request)
        print("\n✅ Orchestrator Result:")
        print(result)
        
        if result["intent"] == "product_search" and "Blue Floral Dress" in result["response"]:
            print("\n🎉 TEST PASSED: Orchestrator correctly handled the message!")
        else:
            print("\n❌ TEST FAILED: Unexpected response.")
            
    except Exception as e:
        print(f"\n❌ TEST FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
