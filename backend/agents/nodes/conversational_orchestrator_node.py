"""
Conversational Orchestrator Node - Multi-turn dialogue manager
Chats naturally with customers, gathers context, and routes only when ready
"""

from models.schemas import AgentState
from services.gemini_service import gemini_service
from typing import Dict, Any
import json
import re


def clean_json_response(content: str) -> str:
    """Remove markdown code blocks from Gemini response"""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return content.strip()


async def extract_context(user_message: str, state: AgentState) -> Dict[str, Any]:
    """
    Extract structured information from user's message
    Updates: product_type, color, occasion, style, size, etc.
    """
    
    prompt = f"""Extract information from this customer message:
"{user_message}"

Previous context we've gathered:
{json.dumps(state.gathered_context, indent=2)}

Extract any of these if EXPLICITLY mentioned:
- product_type: dress, top, pants, jacket, shoes, skirt, etc.
- color: red, blue, black, white, green, yellow, etc.
- occasion: wedding, party, work, casual, formal, gym, date, etc.
- style: elegant, casual, trendy, classic, professional, sporty, etc.
- size: XS, S, M, L, XL, XXL
- price_range: budget, affordable, mid-range, premium, luxury

IMPORTANT:
- Only extract what's EXPLICITLY stated
- Don't infer or assume
- Return null for fields not mentioned
- Preserve previous context if not overridden

Return JSON:
{{
  "product_type": "dress" or null,
  "color": "red" or null,
  "occasion": "wedding" or null,
  "style": "elegant" or null,
  "size": "M" or null,
  "price_range": "mid-range" or null
}}
"""
    
    try:
        response = await gemini_service.generate_content(prompt)
        extracted = json.loads(clean_json_response(response))
        
        # Merge with existing context (new non-null values override)
        updated_context = {**state.gathered_context}
        for key, value in extracted.items():
            if value is not None:
                updated_context[key] = value
        
        return updated_context
    
    except Exception as e:
        print(f"❌ Error extracting context: {e}")
        return state.gathered_context


async def should_keep_chatting(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes conversation to decide: keep chatting OR route to specialist
    
    Returns:
    {
        "action": "chat" or "route",
        "reason": "why",
        "confidence": 0.95,
        "next_question": "What color?" (if chatting),
        "route_to": "product_search" (if routing)
    }
    """
    
    conversation_history = state.conversation_history[-5:] if state.conversation_history else []
    context = state.gathered_context
    
    prompt = f"""You are the main assistant for a fashion boutique. Analyze the conversation to decide if you should:
A) Keep chatting to understand better, OR
B) Route to a specialist agent

**Current message:** "{state.user_message}"

**Conversation so far (last 5 messages):**
{json.dumps(conversation_history, indent=2)}

**Context gathered:**
{json.dumps(context, indent=2)}

**Current state:**
- Cart items: {len(state.cart_items) if state.cart_items else 0}
- Products shown: {len(state.found_products) if state.found_products else 0}
- Turns in conversation: {state.turns_in_conversation}

**ROUTING CRITERIA:**

Route to PRODUCT_SEARCH when:
✅ Customer clearly wants to find/browse products
✅ Customer sent an image of clothing
✅ Customer specified: product_type + (color OR occasion OR style)
   Examples: "red dress", "casual top", "dress for wedding", "shoes for gym"

Route to CART when:
✅ Customer says "add to cart", "I'll take it", "I want the [product]"
✅ Customer mentions specific product from shown products

Route to CHECKOUT when:
✅ Customer says "checkout", "buy now", "proceed to payment"
✅ Cart has items AND customer confirms they want to pay

Route to GENERAL_INQUIRY when:
✅ Customer asks about: policies, returns, hours, contact info, location

KEEP CHATTING when:
❌ Greeting only: "hi", "hello", "hey" (unless it's a repeat greeting)
❌ Vague request: "I need something", "show me clothes", "something nice"
❌ Incomplete info: Only "dress" without color/occasion/style
❌ Just browsing: "what do you have?", "show me options"
❌ Uncertain: "I'm not sure", "maybe", "I don't know"

**Context Analysis:**
- Has product_type: {"YES" if context.get('product_type') else "NO"}
- Has color or style: {"YES" if (context.get('color') or context.get('style')) else "NO"}
- Has occasion: {"YES" if context.get('occasion') else "NO"}

**Decision Logic:**
1. What does the customer want to accomplish?
2. Do we have SPECIFIC ENOUGH info to take action?
3. If YES (confidence > 0.8) → ROUTE
4. If NO → CHAT and ask for ONE missing piece

Return ONLY JSON (no markdown):
{{
  "action": "chat" or "route",
  "confidence": 0.0 to 1.0,
  "reason": "brief explanation",
  "route_to": "product_search" or "cart" or "checkout" or "general_inquiry" or null,
  "next_question": "What color are you thinking?" (only if action is chat)
}}
"""
    
    try:
        response = await gemini_service.generate_content(prompt)
        decision = json.loads(clean_json_response(response))
        return decision
    
    except Exception as e:
        print(f"❌ Error in decision logic: {e}")
        # Fallback: keep chatting
        return {
            "action": "chat",
            "confidence": 0.3,
            "reason": "Error occurred, defaulting to chat",
            "route_to": None,
            "next_question": "Could you tell me more about what you're looking for?"
        }


async def generate_conversational_response(state: AgentState, decision: Dict[str, Any]) -> str:
    """
    Generate natural, human-like response that guides the conversation
    """
    
    context = state.gathered_context
    last_messages = state.conversation_history[-3:] if state.conversation_history else []
    customer_name = state.customer_name or ""
    
    prompt = f"""You are a warm, friendly sales assistant at a Kenyan fashion boutique.

**Recent conversation:**
{json.dumps(last_messages, indent=2)}

**Customer just said:** "{state.user_message}"

**What we know so far:**
{json.dumps(context, indent=2)}

**What we need:** {decision.get('next_question', 'More information')}

**Customer name:** {customer_name if customer_name else "Unknown"}

**Your job:** Continue the conversation naturally to gather information.

**Guidelines:**
1. Be warm and personable (use 1-2 emojis max, not every message)
2. Ask ONE clear question at a time (don't overwhelm)
3. Acknowledge what they said before asking next question
4. Use their name occasionally if you know it
5. Keep it brief (2-3 sentences maximum)
6. Sound like a real person, not a robot
7. Be enthusiastic but not pushy

**Response patterns:**

If they gave partial info:
"Love that! [acknowledge their input]. [ask for missing detail]?"

If completely vague:
"I'd love to help! [ask first clarifying question]?"

If they seem unsure:
"No worries! [gentle guidance]. [simple choice question]?"

If greeting:
"Hello! 👋 [welcoming statement]. [what are you looking for]?"

**Context:**
- Turns so far: {state.turns_in_conversation}
- If turns > 3: Be more direct, offer to show options

Generate ONE natural, conversational response:
"""
    
    try:
        response = await gemini_service.generate_content(prompt)
        return response.strip()
    
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return "I'd love to help you find something perfect! What are you looking for today?"


async def conversational_orchestrator_node(state: AgentState) -> AgentState:
    """
    Conversational orchestrator that chats naturally and routes when ready
    
    Flow:
    1. Extract context from user message
    2. Decide: keep chatting or route to specialist?
    3. If chat: generate conversational response
    4. If route: set routing state for graph
    """
    
    print(f"💬 Orchestrator | Msg: '{state.user_message[:60]}...' | Turn: {state.turns_in_conversation + 1}")
    
    # Increment turn counter
    state.turns_in_conversation += 1
    
    # Step 1: Extract context from message
    state.gathered_context = await extract_context(state.user_message, state)
    print(f"📋 Context: {state.gathered_context}")
    
    # Step 2: Decide - chat or route?
    decision = await should_keep_chatting(state)
    state.routing_confidence = decision['confidence']
    
    print(f"🤔 Decision: {decision['action'].upper()} | Confidence: {decision['confidence']:.2f}")
    
    if decision['action'] == 'route' and decision['confidence'] > 0.75:
        # Enough context - route to specialist
        print(f"🎯 Routing to: {decision['route_to']}")
        print(f"📦 With context: {state.gathered_context}")
        
        state.conversation_mode = "routing"
        
        # Map decision to current_step for existing graph routing
        if decision['route_to'] == 'product_search':
            if state.message_type == 'image' and state.image_url:
                state.current_step = "image_analysis"
            else:
                state.current_step = "product_search"
        
        elif decision['route_to'] == 'cart':
            state.current_step = "cart_management"
            state.cart_action = "add"  # Assume add if routing to cart
        
        elif decision['route_to'] == 'checkout':
            state.current_step = "checkout"
        
        elif decision['route_to'] == 'general_inquiry':
            state.current_step = "general_inquiry"
        
        else:
            # Fallback: default to product search
            state.current_step = "product_search"
    
    else:
        # Keep chatting - generate conversational response
        print(f"💬 Continuing conversation | Reason: {decision['reason']}")
        
        state.conversation_mode = "chatting"
        state.agent_response = await generate_conversational_response(state, decision)
        
        print(f"🗣️  Response: '{state.agent_response[:80]}...'")
        
        # Update conversation history
        if state.conversation_history is None:
            state.conversation_history = []
        
        state.conversation_history.append({"role": "user", "content": state.user_message})
        state.conversation_history.append({"role": "model", "content": state.agent_response})
        
        # Stay in greeting step (ends workflow, waits for next message)
        state.current_step = "greeting"
    
    return state
