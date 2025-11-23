"""
Context Builder - Dynamic Prompt Construction
Fetches AI settings from database and builds LLM prompts
"""

from typing import Dict, Any
import logging
from backend.services.ai_settings_service import ai_settings_service

logger = logging.getLogger(__name__)

async def build_prompt(context: Dict[str, Any]) -> str:
    """
    Build dynamic LLM prompt with AI settings from database
    
    Args:
        context: Dict containing business_id, history, inventory, current_message, etc.
    
    Returns:
        Formatted prompt string for LLM
    """
    try:
        business_id = context.get("business_id")
        history = context.get("history", [])
        inventory = context.get("inventory", [])
        current_message = context.get("current_message", "")
        has_image = context.get("has_image", False)
        
        # Fetch AI settings from database
        logger.info(f"Fetching AI settings for boutique: {business_id}")
        ai_settings = await ai_settings_service.get_ai_settings(business_id)
        
        if not ai_settings:
            logger.warning(f"No AI settings found, using defaults")
            system_prompt = "You are a helpful fashion sales assistant."
            tone = "friendly"
        else:
            system_prompt = ai_settings.get("system_prompt", "")
            tone = ai_settings.get("tone", "friendly")
            logger.info(f"Using AI settings version {ai_settings.get('prompt_version')}")
        
        # Build conversation history
        history_text = ""
        if history:
            history_text = "\n\nRECENT CONVERSATION:\n"
            for msg in history[-8:]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                history_text += f"{role.upper()}: {content}\n"
        
        # Build inventory
        inventory_text = ""
        if inventory:
            inventory_text = "\n\nAVAILABLE PRODUCTS:\n"
            for product in inventory[:10]:
                name = product.get("name", "")
                price = product.get("price", 0)
                inventory_text += f"- {name} (KES {price})\n"
        
        # Combine into final prompt
        full_prompt = f"""{system_prompt}

TONE: {tone.upper()}
{history_text}
{inventory_text}

CURRENT CUSTOMER MESSAGE:
{current_message}

INSTRUCTIONS:
- Respond naturally and helpfully
- Keep responses under 1600 characters
- Return JSON: {{"reply_text": "...", "actions": [], "intent": "..."}}
"""
        
        logger.info(f"Prompt built ({len(full_prompt)} chars)")
        return full_prompt
        
    except Exception as e:
        logger.error(f"Error building prompt: {str(e)}")
        return f"You are a helpful assistant.\n\nCustomer: {context.get('current_message', '')}"
