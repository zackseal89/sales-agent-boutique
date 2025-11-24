"""
Model Context Protocol (MCP) Service
Handles fetching of boutique-specific AI settings and user data from Supabase,
ensuring all requests are authenticated with user's JWT to respect RLS.
"""

from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class MCPService:
    """Service for fetching boutique-specific AI context"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        if not self.supabase_url or not self.anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

    def _create_authed_client(self, user_jwt: str) -> Client:
        """Creates a Supabase client authenticated with the user's JWT."""
        client = create_client(self.supabase_url, self.anon_key)
        client.auth.set_session(access_token=user_jwt, refresh_token=user_jwt)
        return client

    async def get_boutique_settings(self, boutique_id: str, user_jwt: str) -> Optional[Dict[str, Any]]:
        """
        Fetches AI settings for a specific boutique.
        RLS policy should ensure the user is part of the boutique.
        """
        try:
            client = self._create_authed_client(user_jwt)
            response = await client.table("boutique_ai_settings").select("*").eq("boutique_id", boutique_id).single().execute()
            return response.data
        except Exception as e:
            print(f"Error fetching boutique settings: {e}")
            return None

    async def get_boutique_users(self, boutique_id: str, user_jwt: str) -> List[Dict[str, Any]]:
        """
        Fetches all users associated with a specific boutique.
        RLS policy should ensure the user making the request is an admin or member of the boutique.
        """
        try:
            client = self._create_authed_client(user_jwt)
            response = await client.table("boutique_users").select("id, user_id, role").eq("boutique_id", boutique_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching boutique users: {e}")
            return []

mcp_service = MCPService()
