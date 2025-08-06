from pydantic import BaseModel, Field, constr, conint
from bson import ObjectId
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageMetadata(BaseModel):
    tokens: Optional[int] = Field(None, description="Token count")
    model: Optional[str] = Field(None, description="AI model used")
    latency_ms: Optional[int] = Field(None, description="Response latency in milliseconds")

class MessageCreate(BaseModel):
    content: constr(min_length=1, max_length=32000) = Field(..., description="Message content")
    use_rag: bool = Field(default=True, description="Whether to use RAG for this message")
    top_k: conint(ge=1, le=20) = Field(default=5, description="Number of context chunks to retrieve")
    temperature: float = Field(default=0.7, ge=0, le=2, description="LLM temperature")

class MessageResponse(BaseModel):
    id: str = Field(..., description="Message ID")
    thread_id: str = Field(..., description="Thread ID")
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    metadata: Optional[MessageMetadata] = Field(None, description="Message metadata")
    created_at: datetime = Field(..., description="Creation timestamp")

class Message(BaseModel):
    """MongoDB Message document schema"""
    thread_id: str  # ObjectId as string
    role: MessageRole
    content: str
    metadata: Optional[MessageMetadata] = Field(default_factory=MessageMetadata)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        } 