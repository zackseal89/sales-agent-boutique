"""
Test script to verify Supabase connection and data
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_service import supabase_service

async def test_connection():
    """Test Supabase connection and query data"""
    
    print("🔍 Testing Supabase connection...\n")
    
    try:
        # Test 1: Get boutique
        print("1️⃣ Fetching test boutique...")
        boutique = await supabase_service.get_boutique("550e8400-e29b-41d4-a716-446655440000")
        if boutique:
            print(f"✅ Found boutique: {boutique['name']}")
            print(f"   Owner: {boutique['owner_name']}")
            print(f"   WhatsApp: {boutique['whatsapp_number']}\n")
        else:
            print("❌ Boutique not found\n")
            return
        
        # Test 2: Get products
        print("2️⃣ Fetching products...")
        products = await supabase_service.get_products("550e8400-e29b-41d4-a716-446655440000")
        print(f"✅ Found {len(products)} products:")
        for product in products:
            print(f"   - {product['name']} (KES {product['price']})")
        print()
        
        # Test 3: Search products
        print("3️⃣ Searching for 'dress'...")
        results = await supabase_service.search_products_by_text(
            "550e8400-e29b-41d4-a716-446655440000",
            "dress"
        )
        print(f"✅ Found {len(results)} matching products:")
        for product in results:
            print(f"   - {product['name']}")
        print()
        
        # Test 4: Create customer
        print("4️⃣ Creating test customer...")
        customer = await supabase_service.get_or_create_customer(
            "550e8400-e29b-41d4-a716-446655440000",
            "254700000000",
            "Test Customer"
        )
        print(f"✅ Customer created/found: {customer['name']} ({customer['whatsapp_number']})\n")
        
        print("🎉 All tests passed! Supabase is connected and working!\n")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
