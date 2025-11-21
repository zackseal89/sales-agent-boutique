"""
WhatsApp Webhook Handler - Receives messages from Twilio
"""

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from typing import Optional
from models.schemas import WhatsAppMessage
from agents.sales_agent import run_agent
from services.supabase_service import supabase_service
from services.whatsapp_service import whatsapp_service

router = APIRouter()

# Default boutique ID (will be dynamic in production with multi-tenancy)
DEFAULT_BOUTIQUE_ID = "550e8400-e29b-41d4-a716-446655440000"

@router.post("/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    NumMedia: str = Form("0"),
    MediaUrl0: Optional[str] = Form(None),
    MediaContentType0: Optional[str] = Form(None),
    MessageSid: str = Form(...)
):
    """
    Webhook endpoint for incoming WhatsApp messages from Twilio
    
    Twilio sends form-encoded data, so we use Form parameters
    """
    
    # Debug logging to file
    with open("webhook_debug.log", "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"📱 Incoming WhatsApp message\n")
        f.write(f"From: {From}\n")
        f.write(f"Body: {Body}\n")
        f.write(f"{'='*60}\n")
    
    print(f"\n{'='*60}")
    print(f"📱 Incoming WhatsApp message")
    print(f"From: {From}")
    print(f"Body: {Body}")
    print(f"Media: {NumMedia}")
    print(f"{'='*60}\n")
    
    try:
        # Parse message
        message = WhatsAppMessage(
            From=From,
            To=To,
            Body=Body,
            NumMedia=NumMedia,
            MediaUrl0=MediaUrl0,
            MediaContentType0=MediaContentType0,
            MessageSid=MessageSid
        )
        
        # Get or create customer
        customer = await supabase_service.get_or_create_customer(
            boutique_id=DEFAULT_BOUTIQUE_ID,
            whatsapp_number=message.clean_from_number,
            name=None  # Will be extracted from conversation later
        )
        
        # Determine message type
        message_type = "image" if message.has_image else "text"
        
        # Run agent
        result = await run_agent(
            boutique_id=DEFAULT_BOUTIQUE_ID,
            customer_id=customer['id'],
            whatsapp_number=message.clean_from_number,
            user_message=message.Body,
            message_type=message_type,
            image_url=message.MediaUrl0 if message.has_image else None,
            customer_name=customer.get('name')
        )
        
        # Log result
        with open("webhook_debug.log", "a", encoding="utf-8") as f:
            f.write(f"🤖 Agent Response: {result}\n")
        
        # Send response via WhatsApp
        if result['images']:
            # Send with product images
            await whatsapp_service.send_message(
                to_number=message.clean_from_number,
                message=result['response'],
                media_urls=result['images'][:1]  # Send first image
            )
        else:
            # Send text only
            await whatsapp_service.send_message(
                to_number=message.clean_from_number,
                message=result['response']
            )
        
        # Twilio expects empty 200 response
        return Response(content="", status_code=200)
        
    except Exception as e:
        # Log error to file
        with open("webhook_debug.log", "a", encoding="utf-8") as f:
            f.write(f"❌ Error processing webhook: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
            f.write(f"\n{'='*60}\n")
            
        print(f"❌ Error processing webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Still return 200 to Twilio to avoid retries
        return Response(content="", status_code=200)

@router.get("/whatsapp")
async def whatsapp_webhook_get():
    """GET endpoint for webhook verification"""
    return {"status": "WhatsApp webhook is active"}
