from pydantic import BaseModel, Field, constr
from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from uuid import uuid4

class FileStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class TextChunk(BaseModel):
    sequence: str = Field(default_factory=lambda: str(uuid4()), description="Unique chunk identifier")
    text: str = Field(..., description="Text content of the chunk")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the chunk")

class FileUpload(BaseModel):
    title: Optional[constr(min_length=1, max_length=200)] = Field(None, description="Optional file title")

class FileResponse(BaseModel):
    id: str = Field(..., description="File ID")
    workspace_id: str = Field(..., description="Workspace ID")
    uploader_id: str = Field(..., description="Uploader user ID")
    filename: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    storage_url: str = Field(..., description="Storage URL")
    status: FileStatus = Field(..., description="Processing status")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class File(BaseModel):
    """MongoDB File document schema"""
    workspace_id: str  # ObjectId as string
    uploader_id: str   # ObjectId as string
    filename: str
    mime_type: str
    size: int  # bytes
    storage_url: str
    text_chunks: List[TextChunk] = Field(default_factory=list)
    status: FileStatus = FileStatus.UPLOADED
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        } 