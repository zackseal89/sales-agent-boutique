"""
Test Phase 1 Tools - Interactive testing for all agent tools

This script tests the Phase 1 MVP tools:
1. Product Search
2. Cart Management
3. Inventory Check
4. Payment Initiation
5. Order Tracking
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

async def test_tools():
    """Test all Phase 1 tools through the agent"""
    
    print("\n" + "="*80)
    print("🧪 TESTING PHASE 1 MVP TOOLS")
    print("="*80 + "\n")
    
    # Test 1: Product Search with Filters
    print("📝 Test 1: Product Search with Price Filter")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="Show me dresses under 3000 KES",
        customer_name="Jane"
    )
    print(f"✅ Response: {result['response']}")
    print(f"📦 Found {len(result.get('found_products', []))} products")
    if result.get('found_products'):
        for p in result['found_products'][:3]:
            print(f"   - {p['name']} (KES {p['price']})")
    print()
    
    # Test 2: Add to Cart
    print("📝 Test 2: Add Product to Cart")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="Add the first dress to my cart in size M",
        customer_name="Jane"
    )
    print(f"✅ Response: {result['response']}")
    print()
    
    # Test 3: View Cart
    print("📝 Test 3: View Shopping Cart")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="What's in my cart?",
        customer_name="Jane"
    )
    print(f"✅ Response: {result['response']}")
    print()
    
    # Test 4: Check Inventory
    print("📝 Test 4: Check Product Availability")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="Do you have this in size L?",
        customer_name="Jane"
    )
    print(f"✅ Response: {result['response']}")
    print()
    
    # Test 5: Search by Category
    print("📝 Test 5: Search by Category")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="Show me jackets",
        customer_name="Jane"
    )
    print(f"✅ Response: {result['response']}")
    print(f"📦 Found {len(result.get('found_products', []))} products")
    print()
    
    # Test 6: Order Status (will fail gracefully if no orders)
    print("📝 Test 6: Check Order Status")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="Where is my order ORD-123?",
        customer_name="Jane"
    )
    print(f"✅ Response: {result['response']}")
    print()
    
    # Test 7: View Order History
    print("📝 Test 7: View Order History")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="Show me my previous orders",
        customer_name="Jane"
    )
    print(f"✅ Response: {result['response']}")
    print()
    
    # Test 8: Complex Query (multiple tools)
    print("📝 Test 8: Complex Multi-Tool Query")
    print("-" * 80)
    result = await run_agent(
        boutique_id=BOUTIQUE_ID,
        customer_id=TEST_CUSTOMER_ID,
        whatsapp_number=TEST_WHATSAPP,
        user_message="I need a red dress for a party, budget is 5000 KES",
        customer_name="Jane"
    )
    print(f"✅ Response: {result['response']}")
    print(f"📦 Found {len(result.get('found_products', []))} products")
    print()
    
    print("="*80)
    print("🎉 All Phase 1 tool tests completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_tools())
