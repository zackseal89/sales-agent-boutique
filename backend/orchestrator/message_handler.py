from fastapi import Request, HTTPException
from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime

# Services
from backend.services.supabase_service import supabase_service
from backend.services.ai_settings_service import ai_settings_service

# Orchestrator components
from backend.orchestrator.tool_registry import ToolRegistry
from backend.orchestrator.context_builder import build_prompt
from backend.orchestrator.llm_client import generate_response

# Logger setup
logger = logging.getLogger(__name__)

async def handle_whatsapp_message(request: Request) -> Dict[str, Any]:
    """
    Main orchestrator entry point for WhatsApp messages.
    Replaces LangGraph routing with deterministic logic.
    """
    try:
        # 1. Extract message data
        form_data = await request.form()
        from_number = form_data.get("From")
        to_number = form_data.get("To")
        body = form_data.get("Body", "")
        media_url = form_data.get("MediaUrl0")
        
        logger.info(f"📩 Received message from {from_number}: {body[:50]}...")
        
        # 2. Identify business (from Twilio number)
        # In production, this would query the boutiques table
        # For MVP, we might hardcode or use a default business ID
        business_id = get_business_id_by_phone(to_number)
        
        # 3. Get/create conversation
        # Normalize customer phone number
        customer_phone = normalize_phone_number(from_number)
        conversation = get_or_create_conversation(business_id, customer_phone)
        conversation_id = conversation['id']
        
        # 4. Save customer message
        save_message(conversation_id, "customer", body, media_url)
        
        # 5. Fetch context
        history = get_recent_messages(conversation_id, limit=8)
        # memories = await search_memories(conversation_id, body) # TODO: Implement memory search
        memories = []
        inventory = get_products(business_id)
        
        # 6. Build LLM prompt
        prompt = await build_prompt({
            "history": history,
            "memories": memories,
            "inventory": inventory,
            "business_id": business_id,
            "current_message": body,
            "has_image": bool(media_url),
            "media_url": media_url
        })
        
        # 7. Call LLM (reasoning only)
        # If image is present, we might want to analyze it first or pass it to LLM
        llm_response = await generate_response(prompt, image_url=media_url)
        
        logger.info(f"🧠 LLM Response: {json.dumps(llm_response)}")
        
        # 8. Execute tools
        tool_registry = ToolRegistry()
        action_results = []
        
        for action in llm_response.get("actions", []):
            try:
                tool_name = action.get("tool")
                params = action.get("params", {})
                
                # Inject conversation_id if needed
                if "conversation_id" not in params:
                    params["conversation_id"] = conversation_id
                
                logger.info(f"🛠️ Executing tool: {tool_name}")
                result = await tool_registry.execute(tool_name, params)
                action_results.append(result)
                
            except Exception as e:
                logger.error(f"❌ Tool execution failed: {str(e)}")
                # Continue execution, don't crash
        
        # 9. Get AI settings for response filtering and version logging
        ai_settings = await ai_settings_service.get_ai_settings(business_id)
        prompt_version = ai_settings.get('prompt_version', 1) if ai_settings else 1
        do_not_say = ai_settings.get('do_not_say', []) if ai_settings else []
        
        # 10. Filter response against forbidden phrases
        reply_text = llm_response.get("reply_text", "I'm sorry, I didn't catch that.")
        filtered_reply = filter_response(reply_text, do_not_say)
        
        # 11. Save agent response
        save_message(conversation_id, "agent", filtered_reply)
        
        # 12. Update conversation with prompt version
        update_conversation_version(conversation_id, prompt_version)
        
        # 13. Return response (webhook handler will send via Twilio)
        return {
            "response": filtered_reply,
            "images": [],
            "intent": llm_response.get("intent")
        }

    except Exception as e:
        logger.error(f"❌ Orchestrator error: {str(e)}")
        # Fallback response
        return {
            "response": "I'm having a bit of trouble right now. Could you try again in a moment?",
            "images": [],
            "intent": "error"
        }

# --- Helper Functions ---

def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number from Twilio format to database format
    Twilio sends: whatsapp:+14155238886
    Database has: 254712345678 or +254712345678
    """
    if not phone:
        return ""
    
    # Remove whatsapp: prefix
    phone = phone.replace("whatsapp:", "").strip()
    
    # Remove + prefix for comparison
    phone = phone.replace("+", "").strip()
    
    return phone

def get_business_id_by_phone(phone: str) -> str:
    """Get business ID from WhatsApp number"""
    try:
        # Normalize the phone number
        normalized_phone = normalize_phone_number(phone)
        logger.info(f"Looking up business by phone: {phone} -> normalized: {normalized_phone}")
        
        # Try exact match first
        response = supabase_service.client.table("boutiques").select("id").eq("whatsapp_number", normalized_phone).execute()
        if response.data and len(response.data) > 0:
            logger.info(f"Found business: {response.data[0]['id']}")
            return response.data[0]['id']
        
        # Try with + prefix
        response = supabase_service.client.table("boutiques").select("id").eq("whatsapp_number", f"+{normalized_phone}").execute()
        if response.data and len(response.data) > 0:
            logger.info(f"Found business with + prefix: {response.data[0]['id']}")
            return response.data[0]['id']
            
    except Exception as e:
        logger.warning(f"Failed to lookup business by phone {phone}: {e}")
    
    # Return known default boutique ID
    logger.info("Using default boutique ID")
    return "550e8400-e29b-41d4-a716-446655440000" 

def get_or_create_conversation(business_id: str, customer_phone: str) -> Dict:
    """Get existing conversation or create new one"""
    try:
        # Try to find active conversation
        response = supabase_service.client.table("conversations")\
            .select("*")\
            .eq("boutique_id", business_id)\
            .eq("customer_phone", customer_phone)\
            .eq("status", "active")\
            .execute()
            
        if response.data and len(response.data) > 0:
            return response.data[0]
            
        # Create new
        new_conv = {
            "boutique_id": business_id,
            "customer_phone": customer_phone,
            "status": "active",
            "metadata": {}
        }
        response = supabase_service.client.table("conversations").insert(new_conv).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Failed to get/create conversation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise  # Re-raise to trigger fallback response

def save_message(conversation_id: str, role: str, content: str, media_url: str = None):
    """Save message to database"""
    try:
        msg = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "attachments": [media_url] if media_url else []
        }
        supabase_service.client.table("messages").insert(msg).execute()
    except Exception as e:
        logger.error(f"Failed to save message: {e}")

def get_recent_messages(conversation_id: str, limit: int = 8):
    """Fetch recent chat history"""
    try:
        response = supabase_service.client.table("messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        # Return in chronological order
        return sorted(response.data, key=lambda x: x['created_at']) if response.data else []
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        return []

def get_products(business_id: str):
    """Fetch available products"""
    try:
        response = supabase_service.client.table("products")\
            .select("id, name, price, stock_quantity, sizes, colors")\
            .eq("boutique_id", business_id)\
            .gt("stock_quantity", 0)\
            .limit(10)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Failed to fetch products: {e}")
        return []

def filter_response(response: str, forbidden_phrases: list) -> str:
    """
    Filter response to remove forbidden phrases
    
    Args:
        response: AI generated response
        forbidden_phrases: List of phrases to filter out
        
    Returns:
        Filtered response with forbidden phrases replaced
    """
    if not forbidden_phrases:
        return response
    
    filtered = response
    for phrase in forbidden_phrases:
        # Case-insensitive replacement
        import re
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        filtered = pattern.sub('[filtered]', filtered)
    
    if '[filtered]' in filtered:
        logger.warning(f"⚠️ Filtered forbidden phrases from response")
    
    return filtered

def update_conversation_version(conversation_id: str, prompt_version: int):
    """
    Update conversation with the prompt version used
    
    Args:
        conversation_id: Conversation ID
        prompt_version: Version of AI settings used
    """
    try:
        supabase_service.client.table("conversations")\
            .update({"prompt_version": prompt_version})\
            .eq("id", conversation_id)\
            .execute()
        logger.info(f"📝 Logged prompt version {prompt_version} for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"Failed to update conversation version: {e}")
