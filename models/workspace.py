from pydantic import BaseModel, Field, constr
from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any

class WorkspaceSettings(BaseModel):
    rag_enabled: bool = Field(default=True, description="Enable RAG for this workspace")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of context chunks to retrieve")
    temperature: float = Field(default=0.7, ge=0, le=2, description="LLM temperature setting")

class WorkspaceCreate(BaseModel):
    name: constr(min_length=1, max_length=100, pattern=r"^[\w\s\-]+$") = Field(..., description="Workspace name")

class WorkspaceUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100, pattern=r"^[\w\s\-]+$")] = None
    settings: Optional[WorkspaceSettings] = None

class WorkspaceResponse(BaseModel):
    id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Workspace name")
    owner_id: str = Field(..., description="Owner user ID")
    member_ids: List[str] = Field(default_factory=list, description="Member user IDs")
    doc_count: int = Field(default=0, description="Number of documents")
    storage_used: int = Field(default=0, description="Storage used in bytes")
    settings: WorkspaceSettings = Field(default_factory=WorkspaceSettings)
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class WorkspaceMemberAdd(BaseModel):
    user_id: str = Field(..., description="User ID to add as member")
    role: str = Field(default="member", description="Member role")

class Workspace(BaseModel):
    """MongoDB Workspace document schema"""
    name: str
    owner_id: str  # ObjectId as string
    member_ids: List[str] = Field(default_factory=list)  # List of ObjectIds as strings
    doc_count: int = Field(default=0)
    storage_used: int = Field(default=0)  # bytes
    settings: WorkspaceSettings = Field(default_factory=WorkspaceSettings)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        } 