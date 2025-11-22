"""
PayLink Service - M-Pesa Payment Integration
Handles STK Push requests via PayLink SDK
"""

from paylink import AsyncPayLink
from typing import Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class PaylinkService:
    """Service for handling M-Pesa payments via PayLink"""
    
    def __init__(self):
        """Initialize PayLink client with M-Pesa credentials"""
        # Check if we should use mock mode
        self.mock_mode = (
            os.getenv("MPESA_CONSUMER_KEY") == "your_consumer_key" or
            os.getenv("MPESA_CONSUMER_SECRET") == "your_consumer_secret" or
            os.getenv("ENVIRONMENT") == "development"
        )
        
        if self.mock_mode:
            logger.info("🧪 PayLink service initialized in MOCK MODE (no real payments)")
            self.client = None
            return
        
        try:
            # Get M-Pesa credentials from environment
            mpesa_headers = []
            
            # Add M-Pesa credentials if available
            if os.getenv("MPESA_CONSUMER_KEY"):
                mpesa_headers.append(f"mpesa_consumer_key:{os.getenv('MPESA_CONSUMER_KEY')}")
            if os.getenv("MPESA_CONSUMER_SECRET"):
                mpesa_headers.append(f"mpesa_consumer_secret:{os.getenv('MPESA_CONSUMER_SECRET')}")
            if os.getenv("MPESA_BUSINESS_SHORTCODE"):
                mpesa_headers.append(f"mpesa_business_shortcode:{os.getenv('MPESA_BUSINESS_SHORTCODE')}")
            if os.getenv("MPESA_PASSKEY"):
                mpesa_headers.append(f"mpesa_passkey:{os.getenv('MPESA_PASSKEY')}")
            if os.getenv("MPESA_CALLBACK_URL"):
                mpesa_headers.append(f"mpesa_callback_url:{os.getenv('MPESA_CALLBACK_URL')}")
            if os.getenv("MPESA_ENVIRONMENT"):
                mpesa_headers.append(f"mpesa_environment:{os.getenv('MPESA_ENVIRONMENT')}")
            if os.getenv("MPESA_BASE_URL"):
                mpesa_headers.append(f"mpesa_base_url:{os.getenv('MPESA_BASE_URL')}")
            
            # Initialize PayLink with credentials
            self.client = AsyncPayLink(
                api_key=os.getenv("PAYLINK_API_KEY"),
                project=os.getenv("PAYLINK_PROJECT"),
                tracing=os.getenv("PAYLINK_TRACING"),
                payment_provider=["mpesa"],
                required_headers=mpesa_headers if mpesa_headers else None
            )
            logger.info(f"✅ PayLink service initialized with {len(mpesa_headers)} M-Pesa headers")
        except Exception as e:
            logger.error(f"❌ Failed to initialize PayLink: {e}")
            logger.info("🧪 Falling back to MOCK MODE")
            self.mock_mode = True
            self.client = None
    
    async def initiate_stk_push(
        self,
        phone_number: str,
        amount: int,
        account_reference: str,
        transaction_desc: str = "Purchase"
    ) -> Dict[str, Any]:
        """
        Initiate M-Pesa STK Push payment
        
        Args:
            phone_number: Customer's M-Pesa number (format: 2547XXXXXXXX)
            amount: Amount in KES (whole numbers only)
            account_reference: Reference for transaction (max 12 chars)
            transaction_desc: Description of payment (max 13 chars)
            
        Returns:
            Dict with payment status and reference
        """
        # Mock mode - simulate successful payment
        if self.mock_mode:
            import random
            import time
            
            # Format phone number
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            elif phone_number.startswith("+254"):
                phone_number = phone_number[1:]
            elif not phone_number.startswith("254"):
                phone_number = "254" + phone_number
            
            mock_transaction_id = f"MOCK{int(time.time())}{random.randint(1000, 9999)}"
            
            logger.info(f"🧪 MOCK STK Push: {amount} KES to {phone_number}")
            
            return {
                "success": True,
                "mock": True,
                "transaction_id": mock_transaction_id,
                "phone_number": phone_number,
                "amount": amount,
                "reference": account_reference,
                "message": "Mock payment - no real M-Pesa prompt sent"
            }
        
        if not self.client:
            return {
                "success": False,
                "error": "PayLink client not initialized"
            }
        
        try:
            # Format phone number (ensure it starts with 254)
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            elif phone_number.startswith("+254"):
                phone_number = phone_number[1:]
            elif not phone_number.startswith("254"):
                phone_number = "254" + phone_number
            
            # Prepare parameters
            params = {
                "amount": str(amount),  # Must be string
                "phone_number": phone_number,
                "account_reference": account_reference[:12],  # Max 12 chars
                "transaction_desc": transaction_desc[:13]  # Max 13 chars
            }
            
            logger.info(f"💳 Initiating STK Push: {params}")
            
            # Call PayLink SDK
            response = await self.client.call_tool("stk_push", params)
            
            logger.info(f"✅ STK Push Response: {response}")
            
            return {
                "success": True,
                "response": response,
                "phone_number": phone_number,
                "amount": amount,
                "reference": account_reference
            }
            
        except Exception as e:
            logger.error(f"❌ STK Push failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Verify payment status (if PayLink provides this tool)
        
        Args:
            transaction_id: Transaction reference to verify
            
        Returns:
            Dict with payment status
        """
        # TODO: Implement if PayLink provides verification tool
        logger.warning("Payment verification not yet implemented")
        return {
            "success": False,
            "error": "Verification not implemented"
        }

# Singleton instance
paylink_service = PaylinkService()
