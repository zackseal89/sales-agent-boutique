"""
Boutique AI Agent
This class encapsulates the logic for the AI agent that responds to user input
based on boutique-specific settings.
"""

from typing import Optional, Dict, Any
from backend.services.mcp_service import mcp_service
from backend.utils.ai_model import call_ai_model

class BoutiqueAIAgent:
    """An AI agent that generates responses tailored to a specific boutique."""

    def __init__(self, boutique_id: str, user_jwt: str):
        """
        Initializes the BoutiqueAIAgent.
        Args:
            boutique_id: The ID of the boutique the agent is for.
            user_jwt: The JWT of the user interacting with the agent, for RLS.
        """
        if not boutique_id or not user_jwt:
            raise ValueError("boutique_id and user_jwt are required.")

        self.boutique_id = boutique_id
        self.user_jwt = user_jwt
        self.settings: Optional[Dict[str, Any]] = None

    async def load_settings(self) -> bool:
        """
        Loads the AI settings for the boutique from Supabase using the MCP service.
        Returns:
            True if settings were loaded successfully, False otherwise.
        """
        print(f"Loading AI settings for boutique: {self.boutique_id}...")
        settings_data = await mcp_service.get_boutique_settings(self.boutique_id, self.user_jwt)
        if settings_data:
            self.settings = settings_data
            print("✅ AI settings loaded successfully.")
            return True
        else:
            print(f"⚠️ Could not load AI settings for boutique: {self.boutique_id}.")
            return False

    async def generate_response(self, user_input: str) -> str:
        """
        Generates an AI response based on the user's input and the boutique's settings.
        Args:
            user_input: The input message from the user.
        Returns:
            An AI-generated response string.
        """
        # Load settings if they haven't been loaded yet
        if self.settings is None:
            if not await self.load_settings():
                return "I'm sorry, I'm unable to access my configuration right now."

        # Get tone and general prompt from settings, with defaults
        tone = self.settings.get("tone", "helpful and friendly")
        general_prompt = self.settings.get("general_prompt", "You are a helpful assistant for a fashion boutique.")

        # Construct the final prompt for the AI model
        final_prompt = f"""
        {general_prompt}

        Your tone must be: {tone}.

        Here is the customer's message:
        "{user_input}"

        Please generate a suitable response.
        """

        print(f"Generating AI response for input: '{user_input}'")
        # Call the AI model utility
        response = await call_ai_model(final_prompt)
        print(f"🤖 AI Response: {response}")

        return response
