"""
Pydantic models for the application
"""
from .user import User, UserCreate
from .message import Message, MessageCreate, WhatsAppWebhook, WhatsAppMessage
from .department import Department, DepartmentCreate

__all__ = [
    "User",
    "UserCreate",
    "Message",
    "MessageCreate",
    "WhatsAppWebhook",
    "WhatsAppMessage",
    "Department",
    "DepartmentCreate",
]
