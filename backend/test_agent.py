"""
Test the AI agent locally without WhatsApp
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.sales_agent import run_agent

# Test boutique and customer
BOUTIQUE_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_CUSTOMER_ID = "test-customer-123"
TEST_WHATSAPP = "+254700000000"

async def test_agent():
    """Test the agent with various scenarios"""
    
    print("\n" + "="*80)
    print("🧪 TESTING FASHION BOUTIQUE AI AGENT")
    print("="*80 + "\n")
    
    # Test 1: Greeting
    print("📝 Test 1: Greeting")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="Hi there!",
        customer_name="John"
    )
    print(f"✅ Response: {result['response']}\n")
    
    # Test 2: Text search for dress
    print("📝 Test 2: Search for 'dress'")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="I'm looking for a dress",
        customer_name="John"
    )
    print(f"✅ Response: {result['response']}")
    print(f"📦 Found {len(result['found_products'])} products")
    for p in result['found_products']:
        print(f"   - {p['name']} (KES {p['price']})")
    print()
    
    # Test 3: Search for jacket
    print("📝 Test 3: Search for 'jacket'")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="Do you have any jackets?",
        customer_name="John"
    )
    print(f"✅ Response: {result['response']}")
    print(f"📦 Found {len(result['found_products'])} products")
    for p in result['found_products']:
        print(f"   - {p['name']} (KES {p['price']})")
    print()
    
    # Test 4: Search for something not in stock
    print("📝 Test 4: Search for 'shoes' (not in stock)")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="I need shoes",
        customer_name="John"
    )
    print(f"✅ Response: {result['response']}\n")
    
    print("="*80)
    print("🎉 All tests completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_agent())
