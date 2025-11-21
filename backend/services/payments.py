"""
Payment service for M-Pesa integration via PayLink

This module handles M-Pesa STK push payments for the boutique platform.
"""

from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
import httpx
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class PaymentsService:
    """Service for handling M-Pesa payments via PayLink"""
    
    def __init__(self):
        self.api_key = os.getenv("PAYLINK_API_KEY")
        self.api_secret = os.getenv("PAYLINK_API_SECRET")
        self.base_url = os.getenv("PAYLINK_BASE_URL", "https://api.paylink.co.ke")
        
        if not self.api_key or not self.api_secret:
            logger.warning("PayLink credentials not configured. Payment features will be disabled.")
    
    async def initiate_stk_push(
        self,
        phone_number: str,
        amount: float,
        reference: str
    ) -> Dict[str, Any]:
        """
        Initiate M-Pesa STK push payment
        
        Args:
            phone_number: Customer's M-Pesa number (254XXXXXXXXX format)
            amount: Amount to charge in KES
            reference: Order reference/ID
        
        Returns:
            Dict with checkout_request_id and status
        """
        
        if not self.api_key:
            # Return mock response for development
            logger.warning("PayLink not configured. Returning mock payment response.")
            return {
                "success": True,
                "checkout_request_id": f"MOCK_{reference}",
                "message": "Mock payment initiated (PayLink not configured)"
            }
        
        try:
            # Ensure phone number is in correct format
            if phone_number.startswith("+"):
                phone_number = phone_number[1:]
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            
            # PayLink API call
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/stk-push",
                    json={
                        "phone_number": phone_number,
                        "amount": int(amount),  # Amount in KES
                        "reference": reference,
                        "description": f"Payment for order {reference}"
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "checkout_request_id": data.get("checkout_request_id"),
                    "message": "Payment request sent successfully"
                }
        
        except httpx.HTTPError as e:
            logger.error(f"PayLink API error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initiate payment"
            }
        except Exception as e:
            logger.error(f"Payment initiation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "An error occurred while processing payment"
            }
    
    async def check_payment_status(
        self,
        checkout_request_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of an M-Pesa payment
        
        Args:
            checkout_request_id: The checkout request ID from STK push
        
        Returns:
            Dict with payment status and details
        """
        
        if not self.api_key:
            # Return mock response for development
            logger.warning("PayLink not configured. Returning mock status.")
            return {
                "status": "completed",
                "mpesa_receipt": "MOCK_RECEIPT_123",
                "message": "Mock payment completed"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/stk-push/{checkout_request_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": data.get("status"),  # pending/completed/failed
                    "mpesa_receipt": data.get("mpesa_receipt"),
                    "amount": data.get("amount"),
                    "message": f"Payment {data.get('status')}"
                }
        
        except httpx.HTTPError as e:
            logger.error(f"PayLink status check error: {str(e)}")
            return {
                "status": "unknown",
                "error": str(e),
                "message": "Failed to check payment status"
            }
        except Exception as e:
            logger.error(f"Payment status check error: {str(e)}")
            return {
                "status": "unknown",
                "error": str(e),
                "message": "An error occurred while checking payment"
            }
    
    async def handle_payment_callback(
        self,
        callback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle payment callback from PayLink webhook
        
        Args:
            callback_data: Webhook payload from PayLink
        
        Returns:
            Processed payment information
        """
        try:
            checkout_request_id = callback_data.get("checkout_request_id")
            status = callback_data.get("status")
            mpesa_receipt = callback_data.get("mpesa_receipt")
            amount = callback_data.get("amount")
            
            logger.info(f"Payment callback received: {checkout_request_id} - {status}")
            
            return {
                "success": True,
                "checkout_request_id": checkout_request_id,
                "status": status,
                "mpesa_receipt": mpesa_receipt,
                "amount": amount
            }
        
        except Exception as e:
            logger.error(f"Payment callback processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
payments_service = PaymentsService()
