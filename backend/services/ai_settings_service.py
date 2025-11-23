"""
AI Settings Service
Manages boutique AI behavior configuration and prompt versioning
"""

from typing import Dict, Any, List, Optional
from backend.services.supabase_service import supabase_service
import logging

logger = logging.getLogger(__name__)

class AISettingsService:
    """Service for managing AI settings and prompt versions"""
    
    async def get_ai_settings(self, boutique_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch AI settings for a boutique
        
        Args:
            boutique_id: UUID of the boutique
            
        Returns:
            Dict with AI settings or None if not found
        """
        try:
            logger.info(f"Fetching AI settings for boutique: {boutique_id}")
            
            response = await supabase_service.client.table("boutique_ai_settings").select("*").eq("boutique_id", boutique_id).single().execute()
            
            if response.data:
                logger.info(f"AI settings found (version {response.data.get('prompt_version')})")
                return response.data
            
            logger.warning(f"No AI settings found for boutique {boutique_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching AI settings: {str(e)}")
            return None
    
    async def update_ai_settings(
        self,
        boutique_id: str,
        system_prompt: Optional[str] = None,
        tone: Optional[str] = None,
        language_style: Optional[str] = None,
        upsell_rules: Optional[List[Dict]] = None,
        do_not_say: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update AI settings for a boutique
        Automatically increments prompt_version and saves to history
        
        Args:
            boutique_id: UUID of the boutique
            system_prompt: Core AI instructions
            tone: Communication tone (friendly, professional, etc.)
            language_style: Language formality (conversational, formal, etc.)
            upsell_rules: List of upsell trigger-action rules
            do_not_say: List of forbidden phrases
            
        Returns:
            Updated AI settings
        """
        try:
            logger.info(f"Updating AI settings for boutique: {boutique_id}")
            
            # Build update payload (only include provided fields)
            update_data = {}
            if system_prompt is not None:
                update_data["system_prompt"] = system_prompt
            if tone is not None:
                update_data["tone"] = tone
            if language_style is not None:
                update_data["language_style"] = language_style
            if upsell_rules is not None:
                update_data["upsell_rules"] = upsell_rules
            if do_not_say is not None:
                update_data["do_not_say"] = do_not_say
            
            if not update_data:
                raise ValueError("No fields provided for update")
            
            # Update settings (trigger will auto-increment version and save history)
            response = await supabase_service.client.table("boutique_ai_settings").update(update_data).eq("boutique_id", boutique_id).execute()
            
            if response.data:
                new_version = response.data[0].get("prompt_version")
                logger.info(f"AI settings updated to version {new_version}")
                return response.data[0]
            
            raise Exception("Update failed - no data returned")
            
        except Exception as e:
            logger.error(f"Error updating AI settings: {str(e)}")
            raise

# Singleton instance
ai_settings_service = AISettingsService()
