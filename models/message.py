"""
Message and WhatsApp webhook models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageBase(BaseModel):
    """Base message model"""
    user_id: str = Field(..., description="User ID (wa_id)")
    content: str = Field(..., description="Message content")
    role: str = Field(default="user", description="Message role: user or assistant")
    url_imagen: Optional[str] = Field(None, description="Image URL if message has image")


class MessageCreate(MessageBase):
    """Model for creating a new message"""
    pass


class Message(MessageBase):
    """Message model with ID and timestamps"""
    id: int = Field(..., description="Message ID")
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# WhatsApp webhook models
class WhatsAppContact(BaseModel):
    """WhatsApp contact information"""
    profile: Dict[str, str] = Field(default_factory=dict)
    wa_id: str = Field(..., description="WhatsApp ID")


class WhatsAppImage(BaseModel):
    """WhatsApp image message"""
    mime_type: Optional[str] = None
    sha256: Optional[str] = None
    id: str = Field(..., description="Media ID")
    caption: Optional[str] = None


class WhatsAppText(BaseModel):
    """WhatsApp text message"""
    body: str = Field(..., description="Message text")


class WhatsAppButton(BaseModel):
    """WhatsApp button response"""
    payload: Optional[str] = None
    text: Optional[str] = None


class WhatsAppInteractive(BaseModel):
    """WhatsApp interactive message (buttons, lists, etc.)"""
    type: str = Field(..., description="Interactive type: button_reply, list_reply, etc.")
    button_reply: Optional[WhatsAppButton] = None


class WhatsAppMessageData(BaseModel):
    """WhatsApp message data"""
    from_: str = Field(..., alias="from", description="Sender phone number")
    id: str = Field(..., description="Message ID")
    timestamp: str = Field(..., description="Message timestamp")
    type: str = Field(..., description="Message type: text, image, button, interactive, etc.")
    text: Optional[WhatsAppText] = None
    image: Optional[WhatsAppImage] = None
    button: Optional[WhatsAppButton] = None  # For direct button responses
    interactive: Optional[WhatsAppInteractive] = None  # For interactive messages


class WhatsAppValue(BaseModel):
    """WhatsApp webhook value"""
    messaging_product: str
    metadata: Dict[str, Any]
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessageData]] = None


class WhatsAppChange(BaseModel):
    """WhatsApp webhook change"""
    value: WhatsAppValue
    field: str


class WhatsAppEntry(BaseModel):
    """WhatsApp webhook entry"""
    id: str
    changes: List[WhatsAppChange]


class WhatsAppWebhook(BaseModel):
    """WhatsApp webhook payload"""
    object: str
    entry: List[WhatsAppEntry]


class WhatsAppMessage(BaseModel):
    """Simplified WhatsApp message for processing"""
    wa_id: str = Field(..., description="WhatsApp user ID")
    message_id: str = Field(..., description="Message ID")
    timestamp: str = Field(..., description="Message timestamp")
    message_type: str = Field(..., description="Type: text or image")
    text: Optional[str] = Field(None, description="Text content")
    image_id: Optional[str] = Field(None, description="Image media ID")
    image_caption: Optional[str] = Field(None, description="Image caption")
    contact_name: Optional[str] = Field(None, description="Contact name")
