"""
Payment Webhook Handler
Receives payment notifications from PayLink/M-Pesa
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/paylink/payment")
async def paylink_payment_callback(request: Request):
    """
    Webhook endpoint for PayLink payment notifications
    
    This receives callbacks when:
    - Payment is successful
    - Payment fails
    - Payment times out
    """
    try:
        # Get raw body
        body = await request.json()
        logger.info(f"💳 Payment callback received: {body}")
        
        # TODO: Update order status in database based on callback
        # TODO: Send WhatsApp confirmation to customer
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"❌ Payment callback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
