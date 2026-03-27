"""
User models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model"""
    id: str = Field(..., description="WhatsApp user ID (wa_id)")
    name: Optional[str] = Field(None, description="User name")
    phone: Optional[str] = Field(None, description="Phone number")


class UserCreate(UserBase):
    """Model for creating a new user"""
    pass


class User(UserBase):
    """User model with timestamps"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
