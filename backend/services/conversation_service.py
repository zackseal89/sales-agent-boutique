"""
Conversation history management for Supabase
"""

from typing import List, Dict, Any

async def save_conversation_message(
    supabase_client,
    customer_id: str,
    role: str,  # 'user' or 'assistant'
    message: str,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Save a conversation message to database"""
    
    message_data = {
        "customer_id": customer_id,
        "role": role,
        "message": message,
        "metadata": metadata or {}
    }
    
    response = supabase_client.table("conversation_history").insert(message_data).execute()
    return response.data[0] if response.data else None


async def get_conversation_history(
    supabase_client,
    customer_id: str,
    limit: int = 10
) -> List[Dict[str, str]]:
    """
    Get recent conversation history for a customer
    
    Returns:
        List of dicts with 'role' and 'content' keys
    """
    
    response = supabase_client.table("conversation_history")\
        .select("role, message, created_at")\
        .eq("customer_id", customer_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    
    if not response.data:
        return []
    
    # Reverse to get chronological order
    messages = reversed(response.data)
    
    # Format for agent
    return [
        {"role": msg["role"], "content": msg["message"]}
        for msg in messages
    ]
