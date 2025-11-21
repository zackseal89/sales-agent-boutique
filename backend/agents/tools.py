"""
Agent Tools - Functions the AI can call to perform actions

This module defines all tools available to the AI agent, including:
- Product search and discovery
- Shopping cart management
- Inventory checking
- Payment processing
- Order tracking
"""

from typing import Dict, Any, List, Optional
from services.supabase_service import supabase_service
import logging

logger = logging.getLogger(__name__)

# =====================================================
# TOOL IMPLEMENTATIONS
# =====================================================

async def search_products_tool(
    boutique_id: str,
    query: str,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Search for products in the boutique's catalog.
    
    Args:
        boutique_id: ID of the boutique to search in
        query: Search query describing the product
        category: Optional category filter (e.g., "dresses", "shoes")
        max_price: Optional maximum price filter in KES
        min_price: Optional minimum price filter in KES
        limit: Maximum number of products to return
    
    Returns:
        Dict with products list and count
    """
    try:
        logger.info(f"Searching products: query='{query}', category={category}, price_range={min_price}-{max_price}")
        
        # Search products
        products = await supabase_service.search_products_by_text(
            boutique_id=boutique_id,
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            limit=limit
        )
        
        return {
            "success": True,
            "products": products,
            "count": len(products),
            "message": f"Found {len(products)} products matching your search"
        }
    
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        return {
            "success": False,
            "products": [],
            "count": 0,
            "error": str(e)
        }


async def add_to_cart_tool(
    customer_id: str,
    product_id: str,
    size: str,
    quantity: int = 1
) -> Dict[str, Any]:
    """
    Add a product to the customer's shopping cart.
    
    Args:
        customer_id: ID of the customer
        product_id: ID of the product to add
        size: Size selection (e.g., "S", "M", "L", "XL")
        quantity: Number of items to add
    
    Returns:
        Dict with cart update status and new cart summary
    """
    try:
        logger.info(f"Adding to cart: customer={customer_id}, product={product_id}, size={size}, qty={quantity}")
        
        # Add to cart
        result = await supabase_service.add_to_cart(
            customer_id=customer_id,
            product_id=product_id,
            size=size,
            quantity=quantity
        )
        
        # Get updated cart summary
        cart = await supabase_service.get_customer_cart(customer_id)
        
        return {
            "success": True,
            "message": f"Added {quantity} item(s) to your cart",
            "cart_item": result,
            "cart_summary": cart
        }
    
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add item to cart"
        }


async def remove_from_cart_tool(
    customer_id: str,
    item_id: str
) -> Dict[str, Any]:
    """
    Remove an item from the customer's shopping cart.
    
    Args:
        customer_id: ID of the customer
        item_id: ID of the cart item to remove
    
    Returns:
        Dict with removal status and updated cart
    """
    try:
        logger.info(f"Removing from cart: customer={customer_id}, item={item_id}")
        
        await supabase_service.remove_from_cart(customer_id, item_id)
        
        # Get updated cart
        cart = await supabase_service.get_customer_cart(customer_id)
        
        return {
            "success": True,
            "message": "Item removed from cart",
            "cart_summary": cart
        }
    
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to remove item from cart"
        }


async def get_cart_summary_tool(customer_id: str) -> Dict[str, Any]:
    """
    Get the current shopping cart summary for a customer.
    
    Args:
        customer_id: ID of the customer
    
    Returns:
        Dict with cart items, totals, and item count
    """
    try:
        logger.info(f"Getting cart summary for customer: {customer_id}")
        
        cart = await supabase_service.get_customer_cart(customer_id)
        
        # Calculate totals
        items = cart.get('items', [])
        subtotal = sum(item['price'] * item['quantity'] for item in items)
        
        return {
            "success": True,
            "total_items": len(items),
            "subtotal": subtotal,
            "currency": "KES",
            "items": items,
            "message": f"You have {len(items)} item(s) in your cart"
        }
    
    except Exception as e:
        logger.error(f"Error getting cart summary: {str(e)}")
        return {
            "success": False,
            "total_items": 0,
            "subtotal": 0,
            "items": [],
            "error": str(e)
        }


async def check_inventory_tool(
    product_id: str,
    size: str
) -> Dict[str, Any]:
    """
    Check if a product is in stock for a specific size.
    
    Args:
        product_id: ID of the product
        size: Size to check availability for
    
    Returns:
        Dict with stock status and quantity available
    """
    try:
        logger.info(f"Checking inventory: product={product_id}, size={size}")
        
        inventory = await supabase_service.check_inventory(product_id, size)
        
        quantity = inventory.get('quantity', 0)
        in_stock = quantity > 0
        
        return {
            "success": True,
            "in_stock": in_stock,
            "quantity_available": quantity,
            "size": size,
            "product_id": product_id,
            "message": f"{'In stock' if in_stock else 'Out of stock'} - {quantity} available"
        }
    
    except Exception as e:
        logger.error(f"Error checking inventory: {str(e)}")
        return {
            "success": False,
            "in_stock": False,
            "quantity_available": 0,
            "error": str(e)
        }


async def initiate_payment_tool(
    customer_id: str,
    phone_number: str,
    amount: float,
    order_id: str
) -> Dict[str, Any]:
    """
    Initiate M-Pesa STK push payment.
    
    Args:
        customer_id: ID of the customer
        phone_number: Customer's M-Pesa phone number (254XXXXXXXXX)
        amount: Amount to charge in KES
        order_id: Order ID for reference
    
    Returns:
        Dict with payment initiation status and checkout request ID
    """
    try:
        logger.info(f"Initiating payment: customer={customer_id}, amount={amount}, order={order_id}")
        
        # Import payment service (will create this later)
        from services.payments import payments_service
        
        result = await payments_service.initiate_stk_push(
            phone_number=phone_number,
            amount=amount,
            reference=order_id
        )
        
        return {
            "success": True,
            "checkout_request_id": result.get('checkout_request_id'),
            "message": "Payment request sent to your phone. Please enter your M-Pesa PIN to complete.",
            "amount": amount,
            "currency": "KES"
        }
    
    except Exception as e:
        logger.error(f"Error initiating payment: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to initiate payment. Please try again."
        }


async def check_payment_status_tool(
    checkout_request_id: str
) -> Dict[str, Any]:
    """
    Check the status of an M-Pesa payment.
    
    Args:
        checkout_request_id: The checkout request ID from payment initiation
    
    Returns:
        Dict with payment status (pending/completed/failed)
    """
    try:
        logger.info(f"Checking payment status: {checkout_request_id}")
        
        from services.payments import payments_service
        
        status = await payments_service.check_payment_status(checkout_request_id)
        
        return {
            "success": True,
            "payment_status": status.get('status'),
            "mpesa_receipt": status.get('mpesa_receipt'),
            "message": f"Payment status: {status.get('status')}"
        }
    
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        return {
            "success": False,
            "payment_status": "unknown",
            "error": str(e)
        }


async def get_order_status_tool(
    order_id: str,
    customer_id: str
) -> Dict[str, Any]:
    """
    Get the status and details of a specific order.
    
    Args:
        order_id: ID of the order
        customer_id: ID of the customer (for verification)
    
    Returns:
        Dict with order details and current status
    """
    try:
        logger.info(f"Getting order status: order={order_id}, customer={customer_id}")
        
        order = await supabase_service.get_order(order_id, customer_id)
        
        if not order:
            return {
                "success": False,
                "message": "Order not found. Please check the order ID."
            }
        
        return {
            "success": True,
            "order": order,
            "order_status": order.get('order_status'),
            "payment_status": order.get('payment_status'),
            "message": f"Order {order_id} is {order.get('order_status')}"
        }
    
    except Exception as e:
        logger.error(f"Error getting order status: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve order information"
        }


async def get_customer_orders_tool(
    customer_id: str,
    status_filter: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get a list of customer's orders.
    
    Args:
        customer_id: ID of the customer
        status_filter: Optional filter by status (pending/confirmed/shipped/delivered)
        limit: Maximum number of orders to return
    
    Returns:
        Dict with list of orders
    """
    try:
        logger.info(f"Getting customer orders: customer={customer_id}, status={status_filter}")
        
        orders = await supabase_service.get_customer_orders(
            customer_id=customer_id,
            status_filter=status_filter,
            limit=limit
        )
        
        return {
            "success": True,
            "orders": orders,
            "count": len(orders),
            "message": f"Found {len(orders)} order(s)"
        }
    
    except Exception as e:
        logger.error(f"Error getting customer orders: {str(e)}")
        return {
            "success": False,
            "orders": [],
            "count": 0,
            "error": str(e)
        }


# =====================================================
# GEMINI FUNCTION SCHEMAS
# =====================================================

TOOL_SCHEMAS = [
    {
        "name": "search_products",
        "description": "Search for fashion products in the boutique's catalog. Use this when the customer asks about products, wants to browse, or describes what they're looking for.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query describing what the customer is looking for (e.g., 'red dress', 'casual jacket')"
                },
                "category": {
                    "type": "string",
                    "description": "Product category to filter by",
                    "enum": ["dresses", "tops", "bottoms", "jackets", "shoes", "accessories", "bags"]
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price in KES"
                },
                "min_price": {
                    "type": "number",
                    "description": "Minimum price in KES"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "add_to_cart",
        "description": "Add a product to the customer's shopping cart. Use this when the customer wants to buy or add an item.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "ID of the product to add"
                },
                "size": {
                    "type": "string",
                    "description": "Size selection (S, M, L, XL, etc.)"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Number of items to add",
                    "default": 1
                }
            },
            "required": ["product_id", "size"]
        }
    },
    {
        "name": "get_cart_summary",
        "description": "Get the customer's current shopping cart with all items and total. Use when customer asks about their cart or what they're buying.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "check_inventory",
        "description": "Check if a product is available in a specific size. Use before adding to cart or when customer asks about availability.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "ID of the product"
                },
                "size": {
                    "type": "string",
                    "description": "Size to check availability for"
                }
            },
            "required": ["product_id", "size"]
        }
    },
    {
        "name": "get_order_status",
        "description": "Get the status of a customer's order. Use when customer asks about their order, delivery, or tracking.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID or order number"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "get_customer_orders",
        "description": "Get a list of all customer's orders. Use when customer wants to see their order history.",
        "parameters": {
            "type": "object",
            "properties": {
                "status_filter": {
                    "type": "string",
                    "description": "Filter orders by status",
                    "enum": ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
                }
            },
            "required": []
        }
    }
]

# =====================================================
# TOOL REGISTRY
# =====================================================

TOOL_FUNCTIONS = {
    "search_products": search_products_tool,
    "add_to_cart": add_to_cart_tool,
    "remove_from_cart": remove_from_cart_tool,
    "get_cart_summary": get_cart_summary_tool,
    "check_inventory": check_inventory_tool,
    "initiate_payment": initiate_payment_tool,
    "check_payment_status": check_payment_status_tool,
    "get_order_status": get_order_status_tool,
    "get_customer_orders": get_customer_orders_tool
}


async def execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a tool by name with given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
        context: Additional context (boutique_id, customer_id, etc.)
    
    Returns:
        Tool execution result
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
    
    # Add context to args where needed
    if tool_name == "search_products":
        tool_args["boutique_id"] = context.get("boutique_id")
    elif tool_name in ["add_to_cart", "remove_from_cart", "get_cart_summary", "get_customer_orders"]:
        tool_args["customer_id"] = context.get("customer_id")
    elif tool_name in ["get_order_status"]:
        tool_args["customer_id"] = context.get("customer_id")
    elif tool_name == "initiate_payment":
        tool_args["customer_id"] = context.get("customer_id")
    
    # Execute the tool
    tool_function = TOOL_FUNCTIONS[tool_name]
    result = await tool_function(**tool_args)
    
    return result
