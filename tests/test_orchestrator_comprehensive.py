import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies BEFORE importing orchestrator
sys.modules['supabase'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['paylink'] = MagicMock()

# Mock services
from backend.services.supabase_service import supabase_service
from backend.services.paylink_service import paylink_service
import google.generativeai as genai

# Setup Mocks
mock_client = MagicMock()
supabase_service.client = mock_client
mock_model = MagicMock()
genai.GenerativeModel = MagicMock(return_value=mock_model)

# Mock PayLink
paylink_service.initiate_stk_push = AsyncMock(return_value={
    "CheckoutRequestID": "ws_CO_123456789",
    "ResponseCode": "0",
    "CustomerMessage": "Success. Request accepted for processing"
})

# Mock Database Responses
# 1. Boutique Lookup
mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute = AsyncMock(return_value=MagicMock(data={
    "id": "boutique-123",
    "name": "Sarah's Boutique",
    "whatsapp_number": "254712345678"
}))

# 2. Conversation Lookup (Active)
mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute = AsyncMock(return_value=MagicMock(data=[{
    "id": "conv-123",
    "boutique_id": "boutique-123",
    "customer_phone": "254700000000",
    "status": "active",
    "metadata": {}
}]))

# 3. Product Lookup
mock_client.table.return_value.select.return_value.eq.return_value.gt.return_value.limit.return_value.execute = AsyncMock(return_value=MagicMock(data=[
    {"id": "prod-1", "name": "Blue Floral Dress", "price": 2500, "stock_quantity": 5, "sizes": ["S", "M", "L"], "colors": ["Blue"]},
    {"id": "prod-2", "name": "Leather Jacket", "price": 4500, "stock_quantity": 2, "sizes": ["L", "XL"], "colors": ["Black"]}
]))

# 4. Cart Lookup (Empty initially)
mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute = AsyncMock(return_value=MagicMock(data=None))

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# Import Orchestrator
from orchestrator.message_handler import handle_whatsapp_message

async def run_test_scenario(scenario_name, message_text, expected_intent):
    print(f"\n🔹 Scenario: {scenario_name}")
    print(f"   User: '{message_text}'")
    
    # Mock LLM Response based on expected intent
    mock_response = MagicMock()
    
    if expected_intent == "product_search":
        response_text = '{"reply_text": "We have a Blue Floral Dress (KES 2,500) and a Leather Jacket (KES 4,500).", "intent": "product_search", "actions": [{"tool": "search_products", "parameters": {"query": "dress"}}]}'
    elif expected_intent == "add_to_cart":
        response_text = '{"reply_text": "I have added the Blue Floral Dress to your cart.", "intent": "add_to_cart", "actions": [{"tool": "add_to_cart", "parameters": {"product_id": "prod-1", "quantity": 1}}]}'
    elif expected_intent == "checkout":
        response_text = '{"reply_text": "I have sent an M-Pesa payment request to your phone.", "intent": "checkout", "actions": [{"tool": "initiate_mpesa_stk", "parameters": {"amount": 2500, "phone_number": "254700000000"}}]}'
    else:
        response_text = '{"reply_text": "Hello! Welcome to Sarah\'s Boutique.", "intent": "greeting", "actions": []}'

    mock_model.generate_content_async = AsyncMock(return_value=MagicMock(text=response_text))

    # Create Request Object
    mock_request = MagicMock()
    mock_request.form = AsyncMock(return_value={
        "From": "whatsapp:+254700000000",
        "To": "whatsapp:+254712345678",
        "Body": message_text
    })

    # Run Handler
    result = await handle_whatsapp_message(mock_request)
    
    print(f"   🤖 Agent: {result['response']}")
    print(f"   🎯 Intent: {result['intent']}")
    
    if result['intent'] == expected_intent:
        print("   ✅ PASS")
    else:
        print(f"   ❌ FAIL (Expected {expected_intent}, got {result['intent']})")

async def test_comprehensive_flow():
    print("🚀 Starting Comprehensive End-to-End Test...")
    
    await run_test_scenario("Greeting", "Hi there", "greeting")
    await run_test_scenario("Search", "Do you have any dresses?", "product_search")
    await run_test_scenario("Add to Cart", "I want the blue floral dress", "add_to_cart")
    await run_test_scenario("Checkout", "I'll pay with M-Pesa", "checkout")
    
    print("\n🎉 All scenarios completed!")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_flow())
