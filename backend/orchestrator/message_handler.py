from fastapi import Request, HTTPException
from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime

# Services
from backend.services.supabase_service import supabase_service

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
        business_id = await get_business_id_by_phone(to_number)
        
        # 3. Get/create conversation
        conversation = await get_or_create_conversation(business_id, from_number)
        conversation_id = conversation['id']
        
        # 4. Save customer message
        await save_message(conversation_id, "customer", body, media_url)
        
        # 5. Fetch context
        history = await get_recent_messages(conversation_id, limit=8)
        # memories = await search_memories(conversation_id, body) # TODO: Implement memory search
        memories = []
        inventory = await get_products(business_id)
        
        # 6. Build LLM prompt
        prompt = build_prompt({
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
        
        # 9. Save agent response
        reply_text = llm_response.get("reply_text", "I'm sorry, I didn't catch that.")
        await save_message(conversation_id, "agent", reply_text)
        
        # 10. Return response (webhook handler will send via Twilio)
        # The webhook router in api/webhooks.py expects a specific format or handles sending
        # For now, we return the text so the router can send it
        return {
            "response": reply_text,
            "images": [], # TODO: Extract images from tool results if any
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

async def get_business_id_by_phone(phone: str) -> str:
    """Get business ID from WhatsApp number"""
    # TODO: Implement DB lookup
    # For now return a placeholder or query DB
    try:
        response = await supabase_service.client.table("boutiques").select("id").eq("whatsapp_number", phone).single().execute()
        if response.data:
            return response.data['id']
    except:
        pass
    
    # Fallback for dev/testing
    return "00000000-0000-0000-0000-000000000000" 

async def get_or_create_conversation(business_id: str, customer_phone: str) -> Dict:
    """Get existing conversation or create new one"""
    try:
        # Try to find active conversation
        response = await supabase_service.client.table("conversations")\
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
        response = await supabase_service.client.table("conversations").insert(new_conv).execute()
        return response.data[0]
    except Exception as e:
        logger.error(f"Failed to get/create conversation: {e}")
        # Return dummy for dev if DB fails
        return {"id": "00000000-0000-0000-0000-000000000000"}

async def save_message(conversation_id: str, role: str, content: str, media_url: str = None):
    """Save message to database"""
    try:
        msg = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "attachments": [media_url] if media_url else []
        }
        await supabase_service.client.table("messages").insert(msg).execute()
    except Exception as e:
        logger.error(f"Failed to save message: {e}")

async def get_recent_messages(conversation_id: str, limit: int = 8):
    """Fetch recent chat history"""
    try:
        response = await supabase_service.client.table("messages")\
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

async def get_products(business_id: str):
    """Fetch available products"""
    try:
        response = await supabase_service.client.table("products")\
            .select("id, name, price, stock_quantity, sizes, colors")\
            .eq("boutique_id", business_id)\
            .gt("stock_quantity", 0)\
            .limit(10)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Failed to fetch products: {e}")
        return []
