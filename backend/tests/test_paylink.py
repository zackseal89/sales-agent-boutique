import asyncio
import pytest
from services.paylink_service import paylink_service

@pytest.mark.anyio
async def test_paylink():
    """Test PayLink service wrapper"""
    
    # Test STK Push
    result = await paylink_service.initiate_stk_push(
        phone_number="0797357665",  # Test with Kenyan format
        amount=10,
        account_reference="TEST001",
        transaction_desc="Test Payment"
    )

    assert result["success"] is True, f"STK Push failed: {result.get('error')}"
