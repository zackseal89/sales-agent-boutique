"""
MCP Client wrapper for Supabase database operations
Provides a clean interface to the Supabase MCP server
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import json

load_dotenv()

class MCPSupabaseClient:
    """Wrapper around Supabase MCP server for database operations"""
    
    def __init__(self):
        self.project_id = os.getenv("SUPABASE_PROJECT_ID")
        if not self.project_id:
            raise ValueError("SUPABASE_PROJECT_ID must be set in environment variables")
    
    async def execute_sql(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string (use $1, $2 for parameters)
            params: List of parameters to bind to query
            
        Returns:
            List of rows as dictionaries
        """
        # Import MCP tools
        from mcp0_execute_sql import mcp0_execute_sql
        
        # Replace %s placeholders with PostgreSQL $1, $2, etc.
        if params:
            for i, _ in enumerate(params, 1):
                query = query.replace('%s', f'${i}', 1)
        
        try:
            result = await mcp0_execute_sql(
                project_id=self.project_id,
                query=query
            )
            
            # Parse result - MCP returns JSON string
            if isinstance(result, str):
                data = json.loads(result)
            else:
                data = result
            
            # Handle different response formats
            if isinstance(data, dict):
                return data.get('data', [])
            elif isinstance(data, list):
                return data
            else:
                return []
                
        except Exception as e:
            print(f"❌ MCP SQL Error: {str(e)}")
            print(f"Query: {query}")
            raise
    
    async def execute_mutation(
        self, 
        query: str, 
        params: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL mutation query
            params: List of parameters
            
        Returns:
            Result dictionary with affected rows
        """
        # For mutations, we use execute_sql but expect different return format
        result = await self.execute_sql(query, params)
        
        # Return first row for INSERT...RETURNING queries
        if result and len(result) > 0:
            return result[0]
        
        return {"affected_rows": len(result) if result else 0}
    
    async def call_function(
        self, 
        function_name: str, 
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Call a PostgreSQL function
        
        Args:
            function_name: Name of the function
            params: Dictionary of parameters
            
        Returns:
            Function result
        """
        # Build function call query
        param_names = list(params.keys())
        param_values = [params[k] for k in param_names]
        
        # Create parameter placeholders
        placeholders = ', '.join([f'{k} := ${i+1}' for i, k in enumerate(param_names)])
        
        query = f"SELECT * FROM {function_name}({placeholders})"
        
        return await self.execute_sql(query, param_values)

# Global instance
mcp_client = MCPSupabaseClient()
