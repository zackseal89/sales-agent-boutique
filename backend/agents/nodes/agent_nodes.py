"""
LangGraph Agent Nodes - Individual processing steps
"""

from models.schemas import AgentState
from services.gemini_service import gemini_service
from services.supabase_service import supabase_service
from typing import Dict, Any

# =====================================================
# NODE: Image Analysis
# =====================================================

async def analyze_image_node(state: AgentState) -> AgentState:
    """Analyze product image using Gemini Vision"""
    
    print(f"🔍 Analyzing image: {state.image_url}")
    
    if not state.image_url:
        state.agent_response = "I didn't receive an image. Could you please send me a photo of what you're looking for?"
        return state
    
    try:
        # Analyze image with Gemini
        analysis = await gemini_service.analyze_product_image(state.image_url)
        state.image_analysis = analysis
        
        # Generate search query from analysis
        search_query = await gemini_service.generate_product_search_query(analysis)
        state.search_query = search_query
        
        print(f"✅ Image analysis complete: {analysis.get('category')} - {analysis.get('style')}")
        print(f"🔎 Search query: {search_query}")
        
        # Move to product search
        state.current_step = "product_search"
        
    except Exception as e:
        print(f"❌ Error analyzing image: {str(e)}")
        state.agent_response = "I had trouble analyzing that image. Could you try sending it again?"
    
    return state

# =====================================================
# NODE: Product Search
# =====================================================

async def search_products_node(state: AgentState) -> AgentState:
    """Search for products matching the query"""
    
    print(f"🔎 Searching products for: {state.search_query}")
    
    try:
        # Search products in database
        products = await supabase_service.search_products_by_text(
            boutique_id=state.boutique_id,
            query=state.search_query or state.user_message,
            limit=5
        )
        
        state.found_products = products
        
        print(f"✅ Found {len(products)} products")
        
        if products:
            state.current_step = "product_recommendation"
        else:
            state.agent_response = "I couldn't find any products matching that. Could you describe what you're looking for in a different way?"
            state.current_step = "greeting"
        
    except Exception as e:
        print(f"❌ Error searching products: {str(e)}")
        state.agent_response = "I had trouble searching for products. Please try again."
    
    return state

# =====================================================
# NODE: Product Recommendation
# =====================================================

async def recommend_products_node(state: AgentState) -> AgentState:
    """Generate conversational product recommendations"""
    
    print(f"💬 Generating recommendations for {len(state.found_products)} products")
    
    try:
        # Generate conversational response
        response = await gemini_service.generate_conversational_response(
            customer_message=state.user_message,
            products=state.found_products,
            customer_name=state.customer_name,
            conversation_history=state.conversation_history
        )
        
        state.agent_response = response
        
        # Add product images to response
        for product in state.found_products[:3]:
            if product.get('image_urls'):
                state.response_images.extend(product['image_urls'][:1])
        
        print(f"✅ Generated response: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {str(e)}")
        # Fallback to simple response
        if state.found_products:
            product_names = [p['name'] for p in state.found_products[:3]]
            state.agent_response = f"I found these items for you: {', '.join(product_names)}. Which one would you like to know more about?"
    
    return state

# =====================================================
# NODE: Handle Cart
# =====================================================

async def handle_cart_node(state: AgentState) -> AgentState:
    """Handle adding items to cart"""
    
    print(f"🛒 Managing cart")
    
    # Check if user is selecting a product
    user_msg_lower = state.user_message.lower()
    
    # Simple cart logic - look for product names in message
    for product in state.found_products:
        if product['name'].lower() in user_msg_lower:
            # Ask for size if not provided
            if not any(size.lower() in user_msg_lower for size in product.get('sizes', [])):
                state.agent_response = f"Great choice! What size would you like for the {product['name']}? Available sizes: {', '.join(product.get('sizes', []))}"
                state.current_step = "size_selection"
                return state
    
    # If we get here, unclear what they want
    state.agent_response = "Which product would you like to add to your cart? Just tell me the name!"
    
    return state

# =====================================================
# NODE: Greeting / Router
# =====================================================

async def greeting_node(state: AgentState) -> AgentState:
    """Initial greeting and route to appropriate flow"""
    
    print(f"👋 Processing message: {state.user_message[:50]}...")
    
    user_msg_lower = state.user_message.lower()
    
    # Check if it's a greeting
    greetings = ["hi", "hello", "hey", "jambo", "habari", "sasa"]
    if any(g in user_msg_lower for g in greetings):
        name_part = f" {state.customer_name}" if state.customer_name else ""
        state.agent_response = f"Hello{name_part}! 👋 Welcome to our boutique! I can help you find the perfect outfit. You can send me a photo of what you're looking for, or just describe it to me!"
        return state
    
    # Check if they're asking about cart/checkout
    if any(word in user_msg_lower for word in ["cart", "checkout", "buy", "purchase", "order"]):
        if state.cart_items:
            state.current_step = "checkout"
        else:
            state.agent_response = "Your cart is empty! Let me help you find something amazing. Send me a photo or describe what you're looking for!"
        return state
    
    # If we have an image, analyze it
    if state.message_type == "image" and state.image_url:
        state.current_step = "image_analysis"
        return state
    
    # Otherwise, treat as text search
    state.search_query = state.user_message
    state.current_step = "product_search"
    
    return state

# =====================================================
# NODE: Tool-Enabled Conversation
# =====================================================

async def tool_conversation_node(state: AgentState) -> AgentState:
    """
    Handle conversation with tool calling enabled.
    Uses Gemini to decide which tools to call based on user message.
    """
    
    print(f"🤖 Tool-enabled conversation")
    
    try:
        from services.gemini_service import gemini_service
        from agents.tools import TOOL_SCHEMAS
        
        # Build context for tool execution
        context = {
            "boutique_id": state.boutique_id,
            "customer_id": state.customer_id,
            "whatsapp_number": state.whatsapp_number
        }
        
        # Chat with tools
        result = await gemini_service.chat_with_tools(
            message=state.user_message,
            tools=TOOL_SCHEMAS,
            context=context,
            conversation_history=state.conversation_history
        )
        
        # Update state
        state.agent_response = result["response"]
        state.conversation_history = result["conversation_history"]
        state.tool_results = {
            "tool_calls": result["tool_calls"]
        }
        
        # If tools were called, extract relevant data
        for tool_call in result["tool_calls"]:
            tool_name = tool_call["name"]
            tool_result = tool_call["result"]
            
            # Update state based on tool results
            if tool_name == "search_products" and tool_result.get("success"):
                state.found_products = tool_result.get("products", [])
                # Add product images to response
                for product in state.found_products[:3]:
                    if product.get('image_urls'):
                        state.response_images.extend(product['image_urls'][:1])
            
            elif tool_name == "add_to_cart" and tool_result.get("success"):
                cart_summary = tool_result.get("cart_summary", {})
                state.cart_items = cart_summary.get("items", [])
            
            elif tool_name == "get_cart_summary" and tool_result.get("success"):
                state.cart_items = tool_result.get("items", [])
        
        print(f"✅ Tool conversation complete: {len(result['tool_calls'])} tools called")
        
    except Exception as e:
        print(f"❌ Error in tool conversation: {str(e)}")
        state.agent_response = "I had trouble processing that. Could you try rephrasing?"
    
    return state

