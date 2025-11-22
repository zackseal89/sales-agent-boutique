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
    else:
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
    
    # Update conversation history if we have a response (failure case)
    if state.agent_response:
        if state.conversation_history is None:
            state.conversation_history = []
        state.conversation_history.append({"role": "user", "content": state.user_message})
        state.conversation_history.append({"role": "model", "content": state.agent_response})
    
    return state

# =====================================================
# NODE: Product Search
# =====================================================

async def search_products_node(state: AgentState) -> AgentState:
    """Search for products matching the query - Enhanced with LLM reasoning"""
    
    user_query = state.search_query or state.user_message
    print(f"🔎 Searching products for: {user_query}")
    
    try:
        # Use LLM to understand if user wants to see all products or specific items
        from services.gemini_service import gemini_service
        
        understanding_prompt = f"""Analyze this user query: "{user_query}"

Is the user asking to:
A) See ALL products / browse the catalog (general browsing)
B) Search for SPECIFIC products (has keywords like color, style, type)

Respond with ONLY "ALL" or "SPECIFIC".
If they mention ANY product attribute (dress, red, casual, etc.), respond "SPECIFIC".
Examples:
- "what products do you have" → ALL
- "show me everything" → ALL
- "red dress" → SPECIFIC
- "casual clothes" → SPECIFIC"""

        intent = await gemini_service.generate_content(understanding_prompt)
        intent = intent.strip().upper()
        
        print(f"🧠 LLM classified search intent as: {intent}")
        
        if intent == "ALL":
            # User wants to browse all products
            products = await supabase_service.get_products(
                boutique_id=state.boutique_id,
                limit=10
            )
            search_type = "browsing all products"
        else:
            # User wants specific products - use text search
            products = await supabase_service.search_products_by_text(
                boutique_id=state.boutique_id,
                query=user_query,
                limit=5
            )
            search_type = "searching for specific items"
        
        state.found_products = products
        
        print(f"✅ Found {len(products)} products ({search_type})")
        
        if products:
            state.current_step = "product_recommendation"
        else:
            # Use LLM to generate helpful fallback
            fallback_prompt = f"""The user asked: "{user_query}"
We couldn't find any matching products in our boutique.

Generate a friendly, helpful response that:
1. Apologizes politely
2. Suggests they try describing it differently
3. Keeps it brief (1-2 sentences)

Response:"""
            
            state.agent_response = await gemini_service.generate_content(fallback_prompt)
            state.current_step = "greeting"
        
    except Exception as e:
        print(f"❌ Error searching products: {str(e)}")
        import traceback
        traceback.print_exc()
        state.agent_response = "I had trouble searching for products. Please try again."
    
    # Update conversation history if we have a response (failure case or no products)
    if state.agent_response:
        if state.conversation_history is None:
            state.conversation_history = []
        state.conversation_history.append({"role": "user", "content": state.user_message})
        state.conversation_history.append({"role": "model", "content": state.agent_response})
    
    
    return state

# =====================================================
# NODE: Product Recommendation
# =====================================================

async def recommend_products_node(state: AgentState) -> AgentState:
    """Generate personalized product recommendations - Enhanced with LLM reasoning"""
    
    print(f"💡 Generating recommendations for {len(state.found_products)} products")
    
    try:
        from services.gemini_service import gemini_service
        
        # Build product details for LLM
        products_info = []
        for i, product in enumerate(state.found_products[:3], 1):
            products_info.append(f"{i}. {product['name']} - KES {product['price']}")
            if product.get('description'):
                products_info.append(f"   Description: {product['description']}")
        
        products_text = "\n".join(products_info)
        
        # Use LLM to generate natural product presentation
        recommendation_prompt = f"""You are a friendly sales assistant at a fashion boutique in Kenya.

The customer asked: "{state.user_message}"

Here are the products we found:
{products_text}

Generate a warm, natural response that:
1. Presents these products conversationally (not just a list)
2. Highlights features that match what they asked for
3. Invites them to ask questions or add to cart
4. Uses Kenyan English style (friendly, warm, professional)
5. Keeps it concise (2-3 sentences max)

Response:"""
        
        state.agent_response = await gemini_service.generate_content(recommendation_prompt)
        
        # Collect product images (image_urls is an array in database)
        for product in state.found_products[:3]:
            if product.get('image_urls') and len(product['image_urls']) > 0:
                state.response_images.append(product['image_urls'][0])  # Take first image
        
        print(f"✅ Generated personalized recommendation with {len(state.response_images)} images")
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback to simple listing
        product_list = "\n".join([
            f"{i}. {p['name']} - KES {p['price']}" 
            for i, p in enumerate(state.found_products[:3], 1)
        ])
        state.agent_response = f"Here's what I found:\n\n{product_list}\n\nWould you like to add any of these to your cart?"
        state.response_images = [p.get('image_url') for p in state.found_products[:3] if p.get('image_url')]
    
    # Update conversation history
    if state.conversation_history is None:
        state.conversation_history = []
    state.conversation_history.append({"role": "user", "content": state.user_message})
    state.conversation_history.append({"role": "model", "content": state.agent_response})
    
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
                
                # Update conversation history
                if state.conversation_history is None:
                    state.conversation_history = []
                state.conversation_history.append({"role": "user", "content": state.user_message})
                state.conversation_history.append({"role": "model", "content": state.agent_response})
                
                return state
    
    # If we get here, unclear what they want
    state.agent_response = "Which product would you like to add to your cart? Just tell me the name!"
    
    # Update conversation history
    if state.conversation_history is None:
        state.conversation_history = []
    state.conversation_history.append({"role": "user", "content": state.user_message})
    state.conversation_history.append({"role": "model", "content": state.agent_response})
    
    return state

# =====================================================
# NODE: Greeting / Router
# =====================================================

async def general_inquiry_node(state: AgentState) -> AgentState:
    """Handle general inquiries about the boutique (hours, location, etc.)"""
    
    print(f"ℹ️ Handling general inquiry")
    
    try:
        # Fetch boutique info
        info_list = await supabase_service.get_boutique_info(state.boutique_id)
        
        # Format info into context
        info_context = "\n".join([f"{item['category'].upper()}: {item['content']}" for item in info_list])
        
        if not info_context:
            info_context = "No specific store information is available."
            
        # Generate response using Gemini
        # We can reuse the conversational response generator but with specific instructions
        prompt = f"""
        You are a helpful sales assistant for a fashion boutique.
        The customer is asking a general question.
        
        STORE INFORMATION:
        {info_context}
        
        CUSTOMER MESSAGE:
        {state.user_message}
        
        Answer the customer's question based ONLY on the store information provided.
        If the information is not available, politely say you don't know and offer to help with products instead.
        Keep the tone friendly and professional.
        """
        
        response = await gemini_service.generate_content(prompt)
        state.agent_response = response
        
    except Exception as e:
        print(f"❌ Error handling inquiry: {str(e)}")
        state.agent_response = "I'm having trouble retrieving that information right now. Is there anything else I can help you with?"
    
    # Update conversation history
    if state.conversation_history is None:
        state.conversation_history = []
    state.conversation_history.append({"role": "user", "content": state.user_message})
    state.conversation_history.append({"role": "model", "content": state.agent_response})
    
    return state

# =====================================================
# NODE: Greeting / Router
# =====================================================

async def greeting_node(state: AgentState) -> AgentState:
    """Initial greeting and route to appropriate flow"""
    
    print(f"👋 Processing message: {state.user_message[:50]}...")
    
    user_msg_lower = state.user_message.lower()
    
    # Check if it's a greeting (and nothing else substantial)
    import re
    greetings = [r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bjambo\b", r"\bhabari\b", r"\bsasa\b"]
    
    # Only treat as pure greeting if it matches a greeting word AND is short (likely just a greeting)
    is_greeting = any(re.search(g, user_msg_lower) for g in greetings)
    is_short = len(state.user_message.split()) <= 3
    
    if is_greeting and is_short:
        name_part = f" {state.customer_name}" if state.customer_name else ""
        state.agent_response = f"Hello{name_part}! 👋 Welcome to our boutique! I can help you find the perfect outfit. You can send me a photo of what you're looking for, or just describe it to me!"
        
        # Update conversation history
        if state.conversation_history is None:
            state.conversation_history = []
        state.conversation_history.append({"role": "user", "content": state.user_message})
        state.conversation_history.append({"role": "model", "content": state.agent_response})
        
        return state
    
    # Check for "add to cart" commands
    add_cart_keywords = ["add to cart", "add cart", "buy this", "i'll take it", "i want this"]
    if any(keyword in user_msg_lower for keyword in add_cart_keywords):
        state.current_step = "cart_management"
        state.cart_action = "add"
        return state
    
    # Check for "view cart" commands
    view_cart_keywords = ["view cart", "my cart", "show cart", "cart", "what's in my cart"]
    if any(keyword in user_msg_lower for keyword in view_cart_keywords):
        state.current_step = "cart_management"
        state.cart_action = "view"
        return state
    
    # Check for checkout/payment commands
    checkout_keywords = ["checkout", "pay", "buy now", "complete order", "purchase"]
    if any(keyword in user_msg_lower for keyword in checkout_keywords):
        state.current_step = "checkout"
        return state
    
    # Check if they're providing a size (for size selection flow)
    size_options = ["xs", "s", "m", "l", "xl", "xxl", "small", "medium", "large"]
    if state.current_step == "size_selection" and any(size in user_msg_lower for size in size_options):
        # Extract size
        for size in ["xs", "s", "m", "l", "xl", "xxl"]:
            if size in user_msg_lower:
                state.selected_size = size.upper()
                break
        if not state.selected_size:
            if "small" in user_msg_lower:
                state.selected_size = "S"
            elif "medium" in user_msg_lower:
                state.selected_size = "M"
            elif "large" in user_msg_lower:
                state.selected_size = "L"
        
        # Go back to add to cart
        state.current_step = "cart_management"
        state.cart_action = "add"
        return state
    
    # Check for general inquiries
    inquiry_keywords = ["hours", "open", "close", "time", "location", "where", "located", "address", "policy", "return", "contact", "phone", "email", "reach you"]
    if any(keyword in user_msg_lower for keyword in inquiry_keywords):
        state.current_step = "general_inquiry"
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

