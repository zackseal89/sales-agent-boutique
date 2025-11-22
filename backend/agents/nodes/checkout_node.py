"""
Checkout Node - Handle payment and order creation
"""

from models.schemas import AgentState
from services.paylink_service import paylink_service
from services.supabase_service import supabase_service
from services.whatsapp_service import whatsapp_service
import logging

logger = logging.getLogger(__name__)

async def checkout_node(state: AgentState) -> AgentState:
    """
    Handle checkout process:
    1. Calculate cart total
    2. Initiate M-Pesa STK push
    3. Create order in database
    4. Send confirmation
    """
    
    print("💳 Processing checkout...")
    
    try:
        # Get customer's cart
        cart_items = await supabase_service.get_cart(state.customer_id)
        
        if not cart_items:
            state.agent_response = "Your cart is empty! Browse our products and add items before checking out."
            state.current_step = "product_recommendation"
            return state
        
        # Calculate total
        total_amount = sum(item["price"] * item["quantity"] for item in cart_items)
        
        # Get customer phone number
        customer = await supabase_service.get_customer(state.customer_id)
        phone_number = customer.get("phone_number", state.phone_number)
        
        # Generate order reference
        import time
        order_ref = f"ORD{int(time.time())}"
        
        # Initiate STK Push
        payment_result = await paylink_service.initiate_stk_push(
            phone_number=phone_number,
            amount=int(total_amount),
            account_reference=order_ref,
            transaction_desc="Fashion Order"
        )
        
        if payment_result["success"]:
            # Create order in database
            order_data = {
                "customer_id": state.customer_id,
                "total_amount": total_amount,
                "status": "pending_payment",
                "payment_reference": payment_result.get("transaction_id", order_ref),
                "phone_number": phone_number
            }
            
            order = await supabase_service.create_order(order_data)
            
            # Build response message
            if payment_result.get("mock"):
                response = f"🧪 **Mock Payment Initiated**\n\n"
                response += f"Order #{order['id'][:8]}\n"
                response += f"Total: KES {total_amount:,.0f}\n\n"
                response += f"✅ Payment simulated successfully!\n"
                response += f"Transaction ID: {payment_result['transaction_id']}\n\n"
                response += f"_In production, you would receive an M-Pesa prompt on your phone._"
            else:
                response = f"💳 **Payment Request Sent**\n\n"
                response += f"Order #{order['id'][:8]}\n"
                response += f"Total: KES {total_amount:,.0f}\n\n"
                response += f"📱 Please check your phone for the M-Pesa prompt and enter your PIN to complete payment.\n\n"
                response += f"We'll notify you once payment is confirmed!"
            
            state.agent_response = response
            state.current_step = "awaiting_payment"
            
            logger.info(f"✅ Checkout complete: Order {order['id']}, Amount: {total_amount}")
        else:
            state.agent_response = f"❌ Payment failed: {payment_result.get('error', 'Unknown error')}. Please try again or contact support."
            state.current_step = "product_recommendation"
            
    except Exception as e:
        logger.error(f"❌ Checkout error: {e}")
        state.agent_response = "Sorry, there was an error processing your order. Please try again."
        state.current_step = "product_recommendation"
    
    return state
