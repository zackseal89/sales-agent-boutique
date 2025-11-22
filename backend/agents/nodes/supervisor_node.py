"""
Supervisor Node - LLM-based intent classification and routing
Uses Gemini to intelligently route user messages to specialized agents
"""

from models.schemas import AgentState
from services.gemini_service import gemini_service
from typing import Literal

async def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor agent that classifies user intent and routes to appropriate handler
    
    Uses LLM to understand the user's message and determine which specialized
    agent should handle it.
    """
    
    print(f"🧠 Supervisor analyzing message: {state.user_message[:50]}...")
    
    # Build prompt for intent classification
    prompt = f"""You are a routing supervisor for a fashion boutique AI agent.

Analyze the user's message and classify their intent into ONE of these categories:

1. **greeting** - Simple greetings like "hi", "hello", "hey" with no other request
2. **general_info** - Questions about store hours, location, policies, contact info, or store name
3. **product_search** - Looking for products, browsing, asking about specific items
4. **cart** - Adding to cart, viewing cart, removing items
5. **checkout** - Ready to pay, complete purchase, payment

User message: "{state.user_message}"

Respond with ONLY the category name (greeting, general_info, product_search, cart, or checkout).
No explanation, just the category.
"""
    
    try:
        # Use Gemini to classify intent
        response = await gemini_service.generate_content(prompt)
        intent = response.strip().lower()
        
        # Validate and map intent to routing decision
        valid_intents = ["greeting", "general_info", "product_search", "cart", "checkout"]
        
        if intent not in valid_intents:
            print(f"⚠️ Invalid intent '{intent}', defaulting to product_search")
            intent = "product_search"
        
        print(f"✅ Classified intent: {intent}")
        
        # Store intent in state for debugging
        state.intent = intent
        
        # Set routing based on intent
        if intent == "greeting":
            state.current_step = "greeting"
        elif intent == "general_info":
            state.current_step = "general_inquiry"
        elif intent == "product_search":
            # Check if we have an image
            if state.message_type == "image" and state.image_url:
                state.current_step = "image_analysis"
            else:
                state.search_query = state.user_message
                state.current_step = "product_search"
        elif intent == "cart":
            state.current_step = "cart_management"
            # Try to infer cart action
            user_msg_lower = state.user_message.lower()
            if any(keyword in user_msg_lower for keyword in ["add", "buy", "take", "want"]):
                state.cart_action = "add"
            else:
                state.cart_action = "view"
        elif intent == "checkout":
            state.current_step = "checkout"
        
    except Exception as e:
        print(f"❌ Error in supervisor: {str(e)}")
        # Fallback: route to product search
        state.current_step = "product_search"
        state.intent = "error_fallback"
    
    return state
