"""
LangGraph Agent - Main state machine orchestrator
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from models.schemas import AgentState
from agents.nodes.conversational_orchestrator_node import conversational_orchestrator_node
from agents.nodes.agent_nodes import (
    greeting_node,
    analyze_image_node,
    search_products_node,
    recommend_products_node,
    handle_cart_node,
    tool_conversation_node,
    general_inquiry_node
)
from agents.nodes.cart_nodes import add_to_cart_node, view_cart_node
from agents.nodes.checkout_node import checkout_node
from typing import Dict, Any
from datetime import datetime
import os

# =====================================================
# ROUTING LOGIC
# =====================================================

def route_after_supervisor(state: AgentState) -> str:
    """Route after supervisor based on classified intent"""
    if state.current_step == "greeting":
        return "greeting"
    elif state.current_step == "general_inquiry":
        return "general_inquiry"
    elif state.current_step == "image_analysis":
        return "analyze_image"
    elif state.current_step == "product_search":
        return "search_products"
    elif state.current_step == "cart_management":
        return "cart_management"
    elif state.current_step == "checkout":
        return "checkout"
    else:
        # Fallback
        return "search_products"

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

async def cart_management_router(state: AgentState) -> AgentState:
    """Route cart actions to appropriate handlers"""
    if state.cart_action == "add":
        return await add_to_cart_node(state)
    elif state.cart_action == "view":
        return await view_cart_node(state)
    else:
        state.agent_response = "I didn't understand that cart action. Try 'add to cart' or 'view cart'."
        return state

# =====================================================
# BUILD GRAPH
# =====================================================

def create_agent_graph():
    """Create the LangGraph state machine"""
    
    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("conversational_orchestrator", conversational_orchestrator_node)  # NEW: Conversational entry point
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("analyze_image", analyze_image_node)
    workflow.add_node("search_products", search_products_node)
    workflow.add_node("recommend_products", recommend_products_node)
    workflow.add_node("cart_management", cart_management_router)
    workflow.add_node("checkout", checkout_node)
    workflow.add_node("handle_cart", handle_cart_node)
    workflow.add_node("tool_conversation", tool_conversation_node)
    workflow.add_node("general_inquiry", general_inquiry_node)
    
    # Set entry point to conversational orchestrator
    workflow.set_entry_point("conversational_orchestrator")
    
    # Add conditional edges from conversational orchestrator
    workflow.add_conditional_edges(
        "conversational_orchestrator",
        route_after_supervisor,  # Reuse existing routing function
        {
            "greeting": "greeting",
            "general_inquiry": "general_inquiry",
            "analyze_image": "analyze_image",
            "product_search": "search_products",
            "cart_management": "cart_management",
            "checkout": "checkout"
        }
    )
    
    # All specialized nodes now end the workflow
    workflow.add_edge("greeting", END)
    
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
    workflow.add_edge("cart_management", END)
    workflow.add_edge("checkout", END)
    workflow.add_edge("handle_cart", END)
    workflow.add_edge("tool_conversation", END)
    workflow.add_edge("general_inquiry", END)
    
    # Compile graph with checkpointer for conversation memory
    return workflow

# Global cached agent graph
_agent_graph_cache = None

# Initialize checkpointer and agent graph
async def get_agent_graph():
    """Get or create agent graph with checkpointer (cached)"""
    global _agent_graph_cache
    
    # Build connection parameters dictionary (Bypasses URL parsing issues)
    # We decode the password if it was URL encoded in .env, or use raw
    from urllib.parse import unquote
    
    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    if not db_password:
        # Try to extract from URL if password env var missing
        db_url = os.getenv("SUPABASE_DB_URL")
        if db_url and ":" in db_url:
            try:
                # naive parse for fallback
                db_password = db_url.split("@")[0].split(":")[-1]
                db_password = unquote(db_password) # Decode %40 back to @
            except:
                pass
    
    conn_dict = {
        "host": os.getenv("SUPABASE_DB_HOST", "aws-1-eu-west-1.pooler.supabase.com"),
        "port": 6543, # Transaction pooler port
        "user": "postgres.xqaftsmseqzhlfclthyr", # Your project user
        "password": db_password,
        "dbname": "postgres",
        "sslmode": "require"
    }
    
    print(f"🔌 Connecting to DB at {conn_dict['host']}...")
    
    # Create connection pool manually
    from psycopg_pool import AsyncConnectionPool
    
    # Create pool with direct params
    # prepare_threshold=None is CRITICAL for Supabase Transaction Pooler
    # It prevents "prepared statement already exists" errors
    conn_dict["prepare_threshold"] = None
    pool = AsyncConnectionPool(conninfo="", kwargs=conn_dict, max_size=20)
    
    # Create checkpointer with the pool
    checkpointer = AsyncPostgresSaver(pool)
    
    try:
        # Initialize tables
        await checkpointer.setup()
        print("✅ Checkpointer setup complete")
    except Exception as e:
        print(f"❌ Checkpointer setup failed: {e}")
        # Fallback: return graph without checkpointer if DB fails
        # This ensures the bot ALWAYS responds, even if memory fails
        workflow = create_agent_graph()
        return workflow.compile()
    
    # Compile graph with checkpointer
    workflow = create_agent_graph()
    _agent_graph_cache = workflow.compile(checkpointer=checkpointer)
    
    print("✅ Agent graph initialized with conversation memory")
    return _agent_graph_cache

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
    customer_name: str = None,
    conversation_history: list = None,
    config: dict = None
) -> Dict[str, Any]:
    """
    Run the agent with a user message
    
    Args:
        config: Optional config dict with thread_id for conversation persistence
    
    Returns:
        Dict with agent_response and response_images
    """
    
    print(f"\n{'='*60}")
    print(f"🤖 Running agent for customer: {whatsapp_number}")
    print(f"📝 Message: {user_message}")
    if image_url:
        print(f"🖼️  Image: {image_url}")
    if config:
        print(f"🔗 Thread ID: {config.get('configurable', {}).get('thread_id')}")
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
    
    # Get agent graph with checkpointer
    agent_graph = await get_agent_graph()
    
    # Run the graph with config for persistence
    try:
        final_state = await agent_graph.ainvoke(initial_state, config=config)
        
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
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR in agent execution: {str(e)}")
        import traceback
        error_traceback = traceback.format_exc()
        print(error_traceback)
        
        # Log to file for debugging
        with open("agent_crash.log", "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Error: {str(e)}\n")
            f.write(f"Traceback:\n{error_traceback}\n")
            f.write(f"{'='*60}\n")
        
        # Fallback response so user gets SOMETHING
        agent_response = "I'm having a momentary brain freeze! 🧊 Could you please say that again?"
        response_images = []
        found_products = []
        current_step = "greeting"  # Use valid state value instead of "error_fallback"
    
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
