"""
Supabase service using direct SQL execution via MCP server
This replaces the supabase-py client for better performance
"""

from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

# Note: MCP server integration
# The MCP server tools (mcp0_execute_sql, etc.) are available in the AI assistant context
# but not directly callable from Python code. For production use, we have two options:
#
# Option 1: Use supabase-py client (current approach - works but slower)
# Option 2: Use direct PostgreSQL connection with asyncpg (faster, no MCP needed)
#
# For now, we'll use asyncpg for direct database access which gives us
# the performance benefits without needing MCP server integration

import asyncpg

class SupabaseServiceDirect:
    """Service for direct PostgreSQL database access (faster than REST API)"""
    
    def __init__(self):
        # Build PostgreSQL connection string from Supabase credentials
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "")
        
        # Extract project ref from URL (e.g., xqaftsmseqzhlfclthyr from https://xqaftsmseqzhlfclthyr.supabase.co)
        if self.supabase_url:
            project_ref = self.supabase_url.replace("https://", "").replace(".supabase.co", "")
            
            # Supabase PostgreSQL connection details
            # Supabase uses pooler on port 6543 for connection pooling
            # Format: postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
            db_password = os.getenv("SUPABASE_DB_PASSWORD", "")
            
            if db_password:
                # Use transaction mode pooler for better compatibility
                self.connection_string = f"postgresql://postgres.{project_ref}:{db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
                print(f"📊 Database connection: postgres.{project_ref}@pooler.supabase.com")
            else:
                print("⚠️  Warning: SUPABASE_DB_PASSWORD not set")
                self.connection_string = None
        else:
            self.connection_string = None
        
        self._pool = None
    
    async def get_pool(self):
        """Get or create connection pool"""
        if self._pool is None and self.connection_string:
            self._pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
        return self._pool
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query"""
        pool = await self.get_pool()
        
        if not pool:
            print("❌ No database connection available")
            return []
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            # Convert asyncpg.Record to dict
            return [dict(row) for row in rows]
    
    async def execute_mutation(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute INSERT/UPDATE/DELETE with RETURNING"""
        pool = await self.get_pool()
        
        if not pool:
            print("❌ No database connection available")
            return None
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def get_boutique(self, boutique_id: str) -> Optional[Dict[str, Any]]:
        """Get boutique by ID"""
        query = "SELECT * FROM boutiques WHERE id = $1 LIMIT 1"
        results = await self.execute_query(query, boutique_id)
        return results[0] if results else None
    
    async def get_products(self, boutique_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get products for a boutique"""
        query = """
            SELECT * FROM products
            WHERE boutique_id = $1
            AND is_active = true
            ORDER BY created_at DESC
            LIMIT $2
        """
        return await self.execute_query(query, boutique_id, limit)
    
    async def search_products_by_text(
        self, 
        boutique_id: str, 
        query: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search products by text (name, description, category, tags)"""
        
        # Extract keywords from query
        keywords = query.lower().split()
        stop_words = {'i', 'am', 'looking', 'for', 'a', 'an', 'the', 'do', 'you', 'have', 'any', 'need', 'want', 'like'}
        keywords = [k for k in keywords if k not in stop_words and len(k) > 2]
        
        if not keywords:
            keywords = [query]
        
        # Build ILIKE conditions
        conditions = []
        for keyword in keywords:
            pattern = f"%{keyword}%"
            conditions.append(f"(name ILIKE '{pattern}' OR description ILIKE '{pattern}' OR category ILIKE '{pattern}')")
        
        where_clause = " OR ".join(conditions)
        
        sql_query = f"""
            SELECT * FROM products
            WHERE boutique_id = $1
            AND is_active = true
            AND ({where_clause})
            ORDER BY created_at DESC
            LIMIT $2
        """
        
        return await self.execute_query(sql_query, boutique_id, limit)
    
    async def get_or_create_customer(
        self, 
        boutique_id: str, 
        whatsapp_number: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get existing customer or create new one"""
        
        # Try to get existing
        query = """
            SELECT * FROM customers
            WHERE boutique_id = $1
            AND whatsapp_number = $2
            LIMIT 1
        """
        results = await self.execute_query(query, boutique_id, whatsapp_number)
        
        if results:
            return results[0]
        
        # Create new
        insert_query = """
            INSERT INTO customers (boutique_id, whatsapp_number, name)
            VALUES ($1, $2, $3)
            RETURNING *
        """
        result = await self.execute_mutation(insert_query, boutique_id, whatsapp_number, name)
        return result or {}
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        # This would need to be implemented based on order schema
        pass
    
    async def update_order_payment(
        self, 
        order_id: str, 
        payment_status: str,
        mpesa_receipt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update order payment status"""
        query = """
            UPDATE orders
            SET payment_status = $1, mpesa_receipt = $2
            WHERE id = $3
            RETURNING *
        """
        result = await self.execute_mutation(query, payment_status, mpesa_receipt, order_id)
        return result or {}
    
    async def close(self):
        """Close database connection pool"""
        if self._pool:
            await self._pool.close()

# For backward compatibility, create instance with same name
# But note: This requires SUPABASE_DB_PASSWORD to be set
try:
    supabase_service = SupabaseServiceDirect()
except Exception as e:
    print(f"⚠️  Warning: Could not initialize direct database connection: {e}")
    print("⚠️  Falling back to supabase-py client")
    # Fallback to original service
    from services.supabase_service import supabase_service
