"""
Supabase client service for database operations
"""

from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseService:
    """Service for interacting with Supabase database"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.url or not self.service_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.url, self.service_key)
    
    async def get_boutique(self, boutique_id: str) -> Optional[Dict[str, Any]]:
        """Get boutique by ID"""
        response = self.client.table("boutiques").select("*").eq("id", boutique_id).execute()
        return response.data[0] if response.data else None
    
    async def get_products(self, boutique_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get products for a boutique"""
        response = self.client.table("products")\
            .select("*")\
            .eq("boutique_id", boutique_id)\
            .eq("is_active", True)\
            .limit(limit)\
            .execute()
        return response.data
    
    async def get_or_create_customer(
        self, 
        boutique_id: str, 
        whatsapp_number: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get existing customer or create new one"""
        # Try to get existing customer
        response = self.client.table("customers")\
            .select("*")\
            .eq("boutique_id", boutique_id)\
            .eq("whatsapp_number", whatsapp_number)\
            .execute()
        
        if response.data:
            return response.data[0]
        
        # Create new customer
        new_customer = {
            "boutique_id": boutique_id,
            "whatsapp_number": whatsapp_number,
            "name": name
        }
        response = self.client.table("customers").insert(new_customer).execute()
        return response.data[0]
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        response = self.client.table("orders").insert(order_data).execute()
        return response.data[0]
    
    async def update_order_payment(
        self, 
        order_id: str, 
        payment_status: str,
        mpesa_receipt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update order payment status"""
        update_data = {"payment_status": payment_status}
        if mpesa_receipt:
            update_data["mpesa_receipt"] = mpesa_receipt
        
        response = self.client.table("orders")\
            .update(update_data)\
            .eq("id", order_id)\
            .execute()
        return response.data[0]
    
    # =====================================================
    # CART MANAGEMENT
    # =====================================================
    
    async def add_to_cart(
        self,
        customer_id: str,
        product_id: str,
        size: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """Add item to customer's cart or update quantity if exists"""
        
        # Check if item already in cart
        response = self.client.table("cart_items")\
            .select("*")\
            .eq("customer_id", customer_id)\
            .eq("product_id", product_id)\
            .eq("size", size)\
            .execute()
        
        if response.data:
            # Update existing cart item
            existing_item = response.data[0]
            new_quantity = existing_item["quantity"] + quantity
            
            update_response = self.client.table("cart_items")\
                .update({"quantity": new_quantity})\
                .eq("id", existing_item["id"])\
                .execute()
            return update_response.data[0]
        else:
            # Get product details
            product = self.client.table("products")\
                .select("*")\
                .eq("id", product_id)\
                .execute()
            
            if not product.data:
                raise ValueError(f"Product {product_id} not found")
            
            product_data = product.data[0]
            
            # Create new cart item
            cart_item = {
                "customer_id": customer_id,
                "product_id": product_id,
                "product_name": product_data["name"],
                "size": size,
                "quantity": quantity,
                "price": product_data["price"],
                "image_url": product_data.get("image_urls", [None])[0]
            }
            
            insert_response = self.client.table("cart_items")\
                .insert(cart_item)\
                .execute()
            return insert_response.data[0]
    
    async def remove_from_cart(
        self,
        customer_id: str,
        item_id: str
    ) -> bool:
        """Remove item from cart"""
        self.client.table("cart_items")\
            .delete()\
            .eq("id", item_id)\
            .eq("customer_id", customer_id)\
            .execute()
        return True
    
    async def get_customer_cart(self, customer_id: str) -> Dict[str, Any]:
        """Get customer's current cart"""
        response = self.client.table("cart_items")\
            .select("*")\
            .eq("customer_id", customer_id)\
            .execute()
        
        return {
            "items": response.data,
            "customer_id": customer_id
        }
    
    async def update_cart_quantity(
        self,
        item_id: str,
        quantity: int
    ) -> Dict[str, Any]:
        """Update quantity of cart item"""
        response = self.client.table("cart_items")\
            .update({"quantity": quantity})\
            .eq("id", item_id)\
            .execute()
        return response.data[0]
    
    async def clear_cart(self, customer_id: str) -> bool:
        """Clear all items from customer's cart"""
        self.client.table("cart_items")\
            .delete()\
            .eq("customer_id", customer_id)\
            .execute()
        return True
    
    # =====================================================
    # INVENTORY MANAGEMENT
    # =====================================================
    
    async def check_inventory(
        self,
        product_id: str,
        size: str
    ) -> Dict[str, Any]:
        """Check inventory for a product and size"""
        response = self.client.table("inventory")\
            .select("*")\
            .eq("product_id", product_id)\
            .eq("size", size)\
            .execute()
        
        if response.data:
            return response.data[0]
        else:
            # No inventory record means out of stock
            return {
                "product_id": product_id,
                "size": size,
                "quantity": 0
            }
    
    async def update_inventory(
        self,
        product_id: str,
        size: str,
        quantity_change: int
    ) -> Dict[str, Any]:
        """Update inventory quantity (positive to add, negative to subtract)"""
        
        # Get current inventory
        current = await self.check_inventory(product_id, size)
        new_quantity = current.get("quantity", 0) + quantity_change
        
        if new_quantity < 0:
            raise ValueError("Insufficient inventory")
        
        # Update or insert
        if current.get("id"):
            response = self.client.table("inventory")\
                .update({"quantity": new_quantity})\
                .eq("id", current["id"])\
                .execute()
        else:
            response = self.client.table("inventory")\
                .insert({
                    "product_id": product_id,
                    "size": size,
                    "quantity": new_quantity
                })\
                .execute()
        
        return response.data[0]
    
    # =====================================================
    # ORDER MANAGEMENT
    # =====================================================
    
    async def get_order(
        self,
        order_id: str,
        customer_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get order by ID for a specific customer"""
        response = self.client.table("orders")\
            .select("*")\
            .eq("id", order_id)\
            .eq("customer_id", customer_id)\
            .execute()
        
        return response.data[0] if response.data else None
    
    async def get_customer_orders(
        self,
        customer_id: str,
        status_filter: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get customer's orders with optional status filter"""
        query = self.client.table("orders")\
            .select("*")\
            .eq("customer_id", customer_id)\
            .order("created_at", desc=True)\
            .limit(limit)
        
        if status_filter:
            query = query.eq("order_status", status_filter)
        
        response = query.execute()
        return response.data
    
    async def get_order_by_transaction_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get order by transaction ID"""
        response = self.client.table("orders").select("*").eq("transaction_id", transaction_id).single().execute()
        return response.data if response.data else None

    async def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        response = self.client.table("customers").select("*").eq("id", customer_id).single().execute()
        return response.data if response.data else None

    async def update_order_status(
        self,
        order_id: str,
        order_status: str
    ) -> Dict[str, Any]:
        """Update order status"""
        response = self.client.table("orders")\
            .update({"order_status": order_status})\
            .eq("id", order_id)\
            .execute()
        return response.data[0]
    
    # =====================================================
    # ENHANCED PRODUCT SEARCH
    # =====================================================
    
    async def search_products_by_text(
        self, 
        boutique_id: str, 
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search products by text with filters"""
        
        # Extract keywords from query (simple approach)
        keywords = query.lower().split()
        # Remove common words
        stop_words = {'i', 'am', 'looking', 'for', 'a', 'an', 'the', 'do', 'you', 'have', 'any', 'need', 'want', 'like'}
        keywords = [k for k in keywords if k not in stop_words and len(k) > 2]
        
        if not keywords:
            keywords = [query]  # Fallback to full query
        
        # Build search conditions for each keyword
        search_conditions = []
        for keyword in keywords:
            # PostgREST uses * as wildcard in URL syntax, but sometimes % works depending on version
            # The error 'unexpected *' suggests * is not liked.
            # Let's try standard SQL wildcard % but maybe we need to be careful with the string.
            # Actually, let's try to use the 'phraseto_tsquery' or similar if available?
            # No, let's stick to ilike but use the correct wildcard.
            # If * failed, let's try % again.
            search_conditions.append(f"name.ilike.%{keyword}%")
            search_conditions.append(f"description.ilike.%{keyword}%")
            search_conditions.append(f"category.ilike.%{keyword}%")
        
        # Join with OR
        or_condition = ",".join(search_conditions)
        
        # Build query
        query_builder = self.client.table("products")\
            .select("*")\
            .eq("boutique_id", boutique_id)\
            .eq("is_active", True)\
            .or_(or_condition)
        
        # Apply filters
        if category:
            query_builder = query_builder.eq("category", category)
        
        if min_price is not None:
            query_builder = query_builder.gte("price", min_price)
        
        if max_price is not None:
            query_builder = query_builder.lte("price", max_price)
        
        response = query_builder.limit(limit).execute()
        return response.data
    
    # =====================================================
    # GENERAL KNOWLEDGE
    # =====================================================
    
    async def get_boutique_info(self, boutique_id: str) -> List[Dict[str, Any]]:
        """Get general information for a boutique"""
        response = self.client.table("boutique_info")\
            .select("*")\
            .eq("boutique_id", boutique_id)\
            .execute()
        return response.data

# Global instance
supabase_service = SupabaseService()

