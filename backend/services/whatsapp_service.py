"""
Twilio WhatsApp service for sending and receiving messages
"""

from twilio.rest import Client
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class WhatsAppService:
    """Service for sending WhatsApp messages via Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        
        if not self.account_sid or not self.auth_token:
            print("⚠️  Warning: Twilio credentials not set. WhatsApp sending will not work.")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    async def send_message(
        self,
        to_number: str,
        message: str,
        media_urls: Optional[List[str]] = None
    ) -> bool:
        """
        Send a WhatsApp message
        
        Args:
            to_number: Recipient's WhatsApp number (e.g., +254712345678)
            message: Message text
            media_urls: Optional list of image URLs to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        
        if not self.client:
            print(f"📱 [MOCK] Would send to {to_number}: {message}")
            if media_urls:
                print(f"📷 [MOCK] With images: {media_urls}")
            return True
        
        try:
            # Ensure number has whatsapp: prefix
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            # Send message
            message_params = {
                "from_": self.whatsapp_number,
                "to": to_number,
                "body": message
            }
            
            if media_urls:
                message_params["media_url"] = media_urls
            
            twilio_message = self.client.messages.create(**message_params)
            
            print(f"✅ Message sent to {to_number}: {twilio_message.sid}")
            return True
            
        except Exception as e:
            with open("webhook_debug.log", "a", encoding="utf-8") as f:
                f.write(f"❌ Error sending WhatsApp message: {str(e)}\n")
                if hasattr(e, 'code'):
                    f.write(f"   Twilio Error Code: {e.code}\n")
                if hasattr(e, 'msg'):
                    f.write(f"   Twilio Error Message: {e.msg}\n")
            
            print(f"❌ Error sending WhatsApp message: {str(e)}")
            if hasattr(e, 'code'):
                print(f"   Twilio Error Code: {e.code}")
            if hasattr(e, 'msg'):
                print(f"   Twilio Error Message: {e.msg}")
            return False
    
    async def send_product_cards(
        self,
        to_number: str,
        intro_message: str,
        products: List[dict]
    ) -> bool:
        """
        Send product recommendations with images
        
        Args:
            to_number: Recipient's WhatsApp number
            intro_message: Introduction message
            products: List of products to send
        """
        
        # Send intro message
        await self.send_message(to_number, intro_message)
        
        # Send each product with image
        for product in products[:3]:  # Limit to 3 products
            product_message = f"""*{product['name']}*
KES {product['price']:,.0f}

{product.get('description', '')}

Available sizes: {', '.join(product.get('sizes', []))}
Reply with the product name to add to cart! 🛒"""
            
            image_urls = product.get('image_urls', [])
            await self.send_message(
                to_number,
                product_message,
                media_urls=[image_urls[0]] if image_urls else None
            )
        
        return True

# Global instance
whatsapp_service = WhatsAppService()
