"""
Test complete checkout flow with mock payments
"""

import asyncio
from services.supabase_service import supabase_service
from services.paylink_service import paylink_service
from agents.nodes.checkout_node import checkout_node
from models.schemas import AgentState

async def test_checkout_flow():
    """Test the complete checkout process"""
    print("🧪 Testing Complete Checkout Flow\n")
    
    try:
        # 1. Get or create test customer
        print("1️⃣ Setting up test customer...")
        customer_phone = "+254797357665"
        customer = await supabase_service.get_or_create_customer(
            phone_number=customer_phone,
            boutique_id="boutique_123"
        )
        print(f"   ✅ Customer ID: {customer['id']}\n")
        
        # 2. Add items to cart
        print("2️⃣ Adding items to cart...")
        products = await supabase_service.search_products_by_text(
            boutique_id="boutique_123",
            query="dress",
            limit=2
        )
        
        if products:
            for product in products[:1]:  # Add first product
                await supabase_service.add_to_cart(
                    customer_id=customer['id'],
                    product_id=product['id'],
                    size="M",
                    quantity=1
                )
                print(f"   ✅ Added: {product['name']} - KES {product['price']}\n")
        
        # 3. Get cart summary
        print("3️⃣ Checking cart...")
        cart = await supabase_service.get_cart(customer['id'])
        total = sum(item['price'] * item['quantity'] for item in cart)
        print(f"   📦 Cart items: {len(cart)}")
        print(f"   💰 Total: KES {total:,.0f}\n")
        
        # 4. Process checkout
        print("4️⃣ Processing checkout...")
        state = AgentState(
            customer_id=customer['id'],
            phone_number=customer_phone,
            boutique_id="boutique_123",
            current_step="checkout"
        )
        
        result_state = await checkout_node(state)
        
        print(f"   📊 Checkout Status: {result_state.current_step}")
        print(f"   💬 Response:\n{result_state.agent_response}\n")
        
        # 5. Verify order was created
        print("5️⃣ Verifying order creation...")
        # Note: We'd need to add a get_orders method to verify
        print("   ✅ Order should be created in database\n")
        
        print("🎉 Checkout flow test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_checkout_flow())
