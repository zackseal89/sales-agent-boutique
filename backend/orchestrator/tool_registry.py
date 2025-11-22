from typing import Dict, Callable, Any, List
import logging

# Import services
from backend.services.supabase_service import supabase_service
from backend.services.paylink_service import paylink_service

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Central registry for all agent tools.
    Replaces LangGraph nodes with deterministic functions.
    """
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {
            # Product Tools
            "get_inventory": self.get_inventory,
            "search_products": self.search_products,
            
            # Cart Tools
            "add_to_cart": self.add_to_cart,
            "get_cart": self.get_cart,
            
            # Payment Tools
            "initiate_mpesa_stk": self.initiate_mpesa_stk,
            
            # Customer Tools
            "get_customer_profile": self.get_customer_profile,
        }

    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool by name with parameters"""
        if tool_name not in self.tools:
            logger.warning(f"⚠️ Attempted to execute unknown tool: {tool_name}")
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            tool_func = self.tools[tool_name]
            logger.info(f"▶️ Running tool {tool_name} with params: {params}")
            result = await tool_func(**params)
            return result
        except Exception as e:
            logger.error(f"❌ Tool execution error ({tool_name}): {str(e)}")
            return {"error": str(e)}

    # --- Product Tools ---
    
    async def get_inventory(self, product_name: str = None, product_id: str = None, **kwargs):
        """Check stock levels for a product"""
        try:
            query = supabase_service.client.table("products").select("*")
            
            if product_id:
                query = query.eq("id", product_id)
            elif product_name:
                query = query.ilike("name", f"%{product_name}%")
            else:
                return {"error": "Product name or ID required"}
                
            response = await query.single().execute()
            
            # Format response to include sizes/colors in a readable way
            product = response.data
            if product:
                product['attrs'] = {
                    'sizes': product.get('sizes'),
                    'colors': product.get('colors')
                }
            return product
        except Exception as e:
            return {"error": f"Product not found: {e}"}

    async def search_products(self, query: str, **kwargs):
        """Search for products by text"""
        try:
            # Simple text search for MVP
            response = await supabase_service.client.table("products")\
                .select("*")\
                .ilike("name", f"%{query}%")\
                .limit(5)\
                .execute()
            return response.data
        except Exception as e:
            return []

    # --- Cart Tools ---
    
    async def add_to_cart(self, conversation_id: str, product_id: str, quantity: int = 1, **kwargs):
        """Add item to cart (stored in conversation metadata for MVP)"""
        try:
            # 1. Get current metadata
            conv = await supabase_service.client.table("conversations")\
                .select("metadata")\
                .eq("id", conversation_id)\
                .single()\
                .execute()
                
            metadata = conv.data.get("metadata", {}) or {}
            cart = metadata.get("cart", [])
            
            # 2. Add item
            cart.append({
                "product_id": product_id,
                "quantity": quantity,
                "added_at": str(logging.Formatter.converter) # timestamp
            })
            
            metadata["cart"] = cart
            
            # 3. Update DB
            await supabase_service.client.table("conversations")\
                .update({"metadata": metadata})\
                .eq("id", conversation_id)\
                .execute()
                
            return {"status": "success", "message": "Added to cart"}
        except Exception as e:
            return {"error": str(e)}

    async def get_cart(self, conversation_id: str, **kwargs):
        """Get current cart contents"""
        try:
            conv = await supabase_service.client.table("conversations")\
                .select("metadata")\
                .eq("id", conversation_id)\
                .single()\
                .execute()
            
            return conv.data.get("metadata", {}).get("cart", [])
        except Exception as e:
            return []

    # --- Payment Tools ---
    
    async def initiate_mpesa_stk(self, phone: str, amount: float, **kwargs):
        """Initiate M-Pesa STK Push via PayLink"""
        try:
            # Use the existing PayLink service
            # Generate a reference based on timestamp or order ID if available
            import time
            reference = kwargs.get("order_id", f"ORD-{int(time.time())}")
            
            result = await paylink_service.initiate_stk_push(
                phone_number=phone,
                amount=int(amount),
                account_reference=reference,
                transaction_desc="Boutique Purchase"
            )
            
            if result.get("success"):
                return {
                    "status": "pending",
                    "message": "STK Push sent to phone",
                    "checkout_request_id": result.get("transaction_id", "unknown"),
                    "mpesa_reference": result.get("reference")
                }
            else:
                return {
                    "status": "failed",
                    "message": result.get("error", "Payment initiation failed")
                }
        except Exception as e:
            logger.error(f"Payment tool error: {e}")
            return {"status": "failed", "message": str(e)}

    # --- Customer Tools ---
    
    async def get_customer_profile(self, phone: str, **kwargs):
        """Get customer profile and history"""
        # For MVP, just return basic info
        return {
            "phone": phone,
            "segment": "new"
        }
