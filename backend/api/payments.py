"""
Payment Webhook Handler
Receives payment notifications from PayLink/M-Pesa
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging
from backend.services.supabase_service import supabase_service
from backend.services.whatsapp_service import whatsapp_service

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
        
        # Validate payload
        if "status" not in body or "transaction_id" not in body:
            raise HTTPException(status_code=400, detail="Invalid payload")

        # Get order by transaction_id
        order = await supabase_service.get_order_by_transaction_id(body["transaction_id"])
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Update order status in database
        await supabase_service.update_order_status(order["id"], body["status"])

        # Get customer phone number
        customer = await supabase_service.get_customer_by_id(order["customer_id"])
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Send WhatsApp confirmation to customer
        if body["status"] == "success":
            message = f"Your payment for order {order['id']} was successful. Thank you for your purchase!"
        else:
            message = f"Your payment for order {order['id']} failed. Please try again."
        await whatsapp_service.send_message(customer["whatsapp_number"], message)
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"❌ Payment callback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
