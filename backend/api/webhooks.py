"""
WhatsApp Webhook Handler - Receives messages from Twilio
"""

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from typing import Optional
from backend.models.schemas import WhatsAppMessage
from backend.services.supabase_service import supabase_service
from backend.services.whatsapp_service import whatsapp_service

router = APIRouter()

# Default boutique ID (will be dynamic in production with multi-tenancy)
DEFAULT_BOUTIQUE_ID = "550e8400-e29b-41d4-a716-446655440000"

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Webhook endpoint for incoming WhatsApp messages from Twilio
    Uses the new deterministic Orchestrator instead of LangGraph
    """
    
    # Debug logging to file
    with open("webhook_debug.log", "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"📱 Incoming WhatsApp message (Orchestrator)\n")
        f.write(f"{'='*60}\n")
    
    try:
        # Use new orchestrator handler
        from backend.orchestrator.message_handler import handle_whatsapp_message
        
        # Process message
        result = await handle_whatsapp_message(request)
        
        # Log result
        with open("webhook_debug.log", "a", encoding="utf-8") as f:
            f.write(f"🤖 Orchestrator Response: {result}\n")
        
        # Send response via WhatsApp
        # The orchestrator returns the response text, we need to send it via Twilio service
        if result.get('response'):
            # Extract phone number from request form data again
            form_data = await request.form()
            from_number = form_data.get("From")
            
            # Send message
            await whatsapp_service.send_message(
                to_number=from_number,
                message=result['response'],
                media_urls=result.get('images', [])[:1] if result.get('images') else None
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
