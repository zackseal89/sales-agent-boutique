"""
Cart Management Nodes - Handle cart operations
"""

from models.schemas import AgentState
from services.supabase_service import supabase_service
import logging

logger = logging.getLogger(__name__)

async def add_to_cart_node(state: AgentState) -> AgentState:
    """
    Add product to cart
    Handles size selection if needed
    """
    
    print("🛒 Adding to cart...")
    
    try:
        # Check if we have a product selected
        if not state.selected_product_id:
            # Try to get from last recommended products
            if state.found_products:
                state.selected_product_id = state.found_products[0]['id']
            else:
                state.agent_response = "Which product would you like to add to your cart? Please browse our collection first."
                state.current_step = "product_recommendation"
                return state
        
        # Check if size is needed
        product = next((p for p in state.found_products if p['id'] == state.selected_product_id), None)
        
        if not product:
            # Fetch product from database
            # For now, ask user to browse again
            state.agent_response = "I couldn't find that product. Please browse our collection and try again."
            state.current_step = "product_recommendation"
            return state
        
        # Check if size is provided
        if not state.selected_size and product.get('sizes'):
            # Ask for size
            sizes_text = ", ".join(product['sizes'])
            state.agent_response = f"What size would you like for {product['name']}?\n\nAvailable sizes: {sizes_text}"
            state.current_step = "size_selection"
            return state
        
        # Add to cart
        size = state.selected_size or "One Size"
        
        await supabase_service.add_to_cart(
            customer_id=state.customer_id,
            product_id=state.selected_product_id,
            size=size,
            quantity=1
        )
        
        # Get updated cart
        cart = await supabase_service.get_cart(state.customer_id)
        total = sum(item['price'] * item['quantity'] for item in cart)
        
        # Build response
        response = f"✅ **Added to Cart!**\n\n"
        response += f"{product['name']} ({size})\n"
        response += f"Price: KES {product['price']:,.0f}\n\n"
        response += f"📦 Cart Summary:\n"
        response += f"Items: {len(cart)}\n"
        response += f"Total: KES {total:,.0f}\n\n"
        response += f"Ready to checkout? Just say 'checkout' or 'pay now'!"
        
        state.agent_response = response
        state.current_step = "product_recommendation"
        
        # Clear selections
        state.selected_product_id = None
        state.selected_size = None
        
        logger.info(f"✅ Added to cart: {product['name']} ({size})")
        
    except Exception as e:
        logger.error(f"❌ Add to cart error: {e}")
        state.agent_response = "Sorry, I couldn't add that to your cart. Please try again."
        state.current_step = "product_recommendation"
    
    return state


async def view_cart_node(state: AgentState) -> AgentState:
    """
    Display cart contents and total
    """
    
    print("👀 Viewing cart...")
    
    try:
        cart = await supabase_service.get_cart(state.customer_id)
        
        if not cart:
            state.agent_response = "Your cart is empty! 🛒\n\nBrowse our collection and add items you love!"
            state.current_step = "product_recommendation"
            return state
        
        # Build cart summary
        response = "🛒 **Your Cart**\n\n"
        
        total = 0
        for i, item in enumerate(cart, 1):
            item_total = item['price'] * item['quantity']
            total += item_total
            response += f"{i}. {item['product_name']} ({item['size']})\n"
            response += f"   KES {item['price']:,.0f} x {item['quantity']} = KES {item_total:,.0f}\n\n"
        
        response += f"━━━━━━━━━━━━━━━━\n"
        response += f"**Total: KES {total:,.0f}**\n\n"
        response += f"Ready to checkout? Say 'checkout' or 'pay now'!"
        
        state.agent_response = response
        state.current_step = "product_recommendation"
        
    except Exception as e:
        logger.error(f"❌ View cart error: {e}")
        state.agent_response = "Sorry, I couldn't load your cart. Please try again."
        state.current_step = "product_recommendation"
    
    return state
