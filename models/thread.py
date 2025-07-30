from pydantic import BaseModel, Field, constr
from bson import ObjectId
from datetime import datetime
from typing import Optional
from enum import Enum

class ThreadStatus(str, Enum):
    OPEN = "open"
    ARCHIVED = "archived"

class ThreadCreate(BaseModel):
    title: Optional[constr(min_length=1, max_length=120)] = Field(None, description="Thread title")
    workspace_id: Optional[str] = Field(None, description="Optional workspace ID for RAG context")

class ThreadUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=120)] = None
    status: Optional[ThreadStatus] = None
    workspace_id: Optional[str] = None

class ThreadResponse(BaseModel):
    id: str = Field(..., description="Thread ID")
    user_id: str = Field(..., description="Creator user ID")
    title: str = Field(..., description="Thread title")
    workspace_id: Optional[str] = Field(None, description="Optional workspace ID for RAG context")
    status: ThreadStatus = Field(default=ThreadStatus.OPEN, description="Thread status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class Thread(BaseModel):
    """MongoDB Thread document schema"""
    user_id: str       # ObjectId as string - creator/owner of thread
    title: str
    workspace_id: Optional[str] = Field(None, description="Optional workspace reference for RAG")
    status: ThreadStatus = ThreadStatus.OPEN
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        } 