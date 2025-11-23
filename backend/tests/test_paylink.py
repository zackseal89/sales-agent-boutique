import asyncio
from services.paylink_service import paylink_service

async def test_paylink():
    """Test PayLink service wrapper"""
    print("🔍 Testing PayLink Service...")
    
    try:
        # Test STK Push
        result = await paylink_service.initiate_stk_push(
            phone_number="0797357665",  # Test with Kenyan format
            amount=10,
            account_reference="TEST001",
            transaction_desc="Test Payment"
        )
        
        print(f"\n📊 Result: {result}")
        
        if result["success"]:
            print("✅ STK Push initiated successfully!")
        else:
            print(f"❌ Failed: {result.get('error')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_paylink())
