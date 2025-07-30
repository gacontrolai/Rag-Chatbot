from pydantic import BaseModel, Field, EmailStr, constr
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from enum import Enum

class UserPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: constr(min_length=8, max_length=100) = Field(..., description="User password")
    name: constr(min_length=1, max_length=100) = Field(..., description="User full name")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserResponse(BaseModel):
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User name")
    plan: UserPlan = Field(default=UserPlan.FREE, description="User plan")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    plan: Optional[UserPlan] = None

class User(BaseModel):
    """MongoDB User document schema"""
    email: EmailStr
    password_hash: str
    name: str
    plan: UserPlan = UserPlan.FREE
    workspaces: List[str] = Field(default_factory=list)  # List of workspace ObjectIds as strings
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        # Allow ObjectId for _id field
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        } 