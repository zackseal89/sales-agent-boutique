"""
LangGraph Agent - Main state machine orchestrator
"""

from langgraph.graph import StateGraph, END
from models.schemas import AgentState
from agents.nodes.agent_nodes import (
    greeting_node,
    analyze_image_node,
    search_products_node,
    recommend_products_node,
    handle_cart_node,
    tool_conversation_node
)
from typing import Dict, Any

# =====================================================
# ROUTING LOGIC
# =====================================================

def route_after_greeting(state: AgentState) -> str:
    """Route after greeting based on current step"""
    if state.current_step == "image_analysis":
        return "analyze_image"
    elif state.current_step == "product_search":
        return "search_products"
    elif state.current_step == "checkout":
        return "handle_cart"
    elif state.current_step == "tool_execution":
        return "tool_conversation"
    elif state.agent_response:
        # If greeting already set a response, end
        return END
    else:
        # Default: use tool-enabled conversation
        return "tool_conversation"

def route_after_image_analysis(state: AgentState) -> str:
    """Route after image analysis"""
    if state.current_step == "product_search":
        return "search_products"
    else:
        return END

def route_after_search(state: AgentState) -> str:
    """Route after product search"""
    if state.current_step == "product_recommendation":
        return "recommend_products"
    else:
        return END

# =====================================================
# BUILD GRAPH
# =====================================================

def create_agent_graph():
    """Create the LangGraph state machine"""
    
    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("analyze_image", analyze_image_node)
    workflow.add_node("search_products", search_products_node)
    workflow.add_node("recommend_products", recommend_products_node)
    workflow.add_node("handle_cart", handle_cart_node)
    workflow.add_node("tool_conversation", tool_conversation_node)
    
    # Set entry point
    workflow.set_entry_point("greeting")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "greeting",
        route_after_greeting,
        {
            "analyze_image": "analyze_image",
            "search_products": "search_products",
            "handle_cart": "handle_cart",
            "tool_conversation": "tool_conversation",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "analyze_image",
        route_after_image_analysis,
        {
            "search_products": "search_products",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "search_products",
        route_after_search,
        {
            "recommend_products": "recommend_products",
            END: END
        }
    )
    
    # Recommend products ends the flow
    workflow.add_edge("recommend_products", END)
    workflow.add_edge("handle_cart", END)
    workflow.add_edge("tool_conversation", END)
    
    # Compile graph
    return workflow.compile()

# Create global agent instance
agent_graph = create_agent_graph()

# =====================================================
# AGENT RUNNER
# =====================================================

async def run_agent(
    boutique_id: str,
    customer_id: str,
    whatsapp_number: str,
    user_message: str,
    message_type: str = "text",
    image_url: str = None,
    customer_name: str = None
) -> Dict[str, Any]:
    """
    Run the agent with a user message
    
    Returns:
        Dict with agent_response and response_images
    """
    
    print(f"\n{'='*60}")
    print(f"🤖 Running agent for customer: {whatsapp_number}")
    print(f"📝 Message: {user_message}")
    if image_url:
        print(f"🖼️  Image: {image_url}")
    print(f"{'='*60}\n")
    
    # Create initial state
    initial_state = AgentState(
        boutique_id=boutique_id,
        customer_id=customer_id,
        whatsapp_number=whatsapp_number,
        user_message=user_message,
        message_type=message_type,
        image_url=image_url,
        customer_name=customer_name
    )
    
    # Run the graph
    final_state = await agent_graph.ainvoke(initial_state)
    
    # LangGraph returns a dict, not AgentState object
    if isinstance(final_state, dict):
        agent_response = final_state.get('agent_response', '')
        response_images = final_state.get('response_images', [])
        found_products = final_state.get('found_products', [])
        current_step = final_state.get('current_step', '')
    else:
        agent_response = final_state.agent_response
        response_images = final_state.response_images
        found_products = final_state.found_products
        current_step = final_state.current_step
    
    print(f"\n{'='*60}")
    print(f"✅ Agent completed")
    print(f"📤 Response: {agent_response}")
    if response_images:
        print(f"🖼️  Images: {len(response_images)} attached")
    print(f"{'='*60}\n")
    
    return {
        "response": agent_response,
        "images": response_images,
        "found_products": found_products,
        "current_step": current_step
    }
