"""
Pydantic models for the Fashion Boutique AI Agent
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

# =====================================================
# AGENT STATE MODELS
# =====================================================

class AgentState(BaseModel):
    """State for the LangGraph agent"""
    
    # Conversation context
    boutique_id: str
    customer_id: str
    whatsapp_number: str
    conversation_id: Optional[str] = None
    
    # Current message
    user_message: str
    message_type: Literal["text", "image", "audio"] = "text"
    image_url: Optional[str] = None
    
    # Agent state
    current_step: Literal[
        "greeting",
        "image_analysis",
        "product_search",
        "product_recommendation",
        "size_selection",
        "cart_management",
        "checkout",
        "payment",
        "order_confirmation",
        "tool_execution",
        "general_inquiry"
    ] = "greeting"
    
    # Extracted information
    search_query: Optional[str] = None
    image_analysis: Optional[Dict[str, Any]] = None
    found_products: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Shopping cart
    cart_items: List[Dict[str, Any]] = Field(default_factory=list)
    selected_product_id: Optional[str] = None  # Track last viewed/selected product
    selected_size: Optional[str] = None  # Store size selection for cart
    cart_action: Optional[str] = None  # Track cart operation (add, remove, view)
    
    # Customer preferences
    customer_name: Optional[str] = None
    preferred_size: Optional[str] = None
    delivery_address: Optional[str] = None
    
    # Agent response
    agent_response: str = ""
    response_images: List[str] = Field(default_factory=list)
    
    # Supervisor intent classification
    intent: Optional[str] = None  # Classified intent by supervisor
    
    # Conversational Orchestrator fields
    conversation_mode: Literal["chatting", "routing", "specialist_active"] = "chatting"
    gathered_context: Dict[str, Any] = Field(default_factory=dict)  # Rich context from conversation
    routing_confidence: float = 0.0  # 0.0-1.0 confidence for routing decision
    turns_in_conversation: int = 0  # Track conversation depth
    
    # Tool execution
    pending_tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    last_tool_call: Optional[str] = None
    
    # Conversation history (for context)
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)

# =====================================================
# PRODUCT MODELS
# =====================================================

class Product(BaseModel):
    """Product model"""
    id: str
    boutique_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    sizes: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)
    stock_quantity: int = 0
    tags: List[str] = Field(default_factory=list)
    image_urls: List[str] = Field(default_factory=list)
    is_active: bool = True

class CartItem(BaseModel):
    """Cart item model"""
    product_id: str
    product_name: str
    size: str
    color: Optional[str] = None
    quantity: int = 1
    price: float
    image_url: Optional[str] = None

# =====================================================
# WEBHOOK MODELS
# =====================================================

class WhatsAppMessage(BaseModel):
    """WhatsApp incoming message model"""
    From: str  # WhatsApp number (e.g., whatsapp:+254712345678)
    To: str    # Your Twilio WhatsApp number
    Body: str  # Message text
    NumMedia: str = "0"  # Number of media attachments
    MediaUrl0: Optional[str] = None  # First media URL
    MediaContentType0: Optional[str] = None  # Media type
    MessageSid: str  # Twilio message ID
    
    @property
    def clean_from_number(self) -> str:
        """Get clean phone number without 'whatsapp:' prefix"""
        return self.From.replace("whatsapp:", "")
    
    @property
    def has_image(self) -> bool:
        """Check if message has an image"""
        return int(self.NumMedia) > 0 and self.MediaContentType0 and "image" in self.MediaContentType0

# =====================================================
# ORDER MODELS
# =====================================================

class Order(BaseModel):
    """Order model"""
    id: Optional[str] = None
    boutique_id: str
    customer_id: str
    order_number: str
    items: List[CartItem]
    subtotal: float
    delivery_fee: float = 200.0  # Default KES 200
    total_amount: float
    delivery_address: str
    payment_status: Literal["pending", "paid", "failed", "refunded"] = "pending"
    order_status: Literal["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"] = "pending"
    mpesa_receipt: Optional[str] = None
    checkout_request_id: Optional[str] = None
