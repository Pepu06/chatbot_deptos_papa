"""
Department models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    """Base department model"""
    address: str = Field(..., description="Department address")


class DepartmentCreate(DepartmentBase):
    """Model for creating a new department"""
    pass


class Department(DepartmentBase):
    """Department model with ID and timestamps"""
    id: int = Field(..., description="Department ID")
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
