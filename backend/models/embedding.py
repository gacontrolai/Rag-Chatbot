from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
from typing import List

class EmbeddingSearch(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")

class EmbeddingResult(BaseModel):
    sequence: str = Field(..., description="Chunk identifier")
    text: str = Field(..., description="Text content")
    score: float = Field(..., description="Similarity score")
    file_id: str = Field(..., description="Source file ID")

class Embedding(BaseModel):
    """MongoDB Embedding document schema (if using separate collection)"""
    workspace_id: str  # ObjectId as string
    file_id: str       # ObjectId as string
    sequence: str      # UUID as string
    text: str
    vector: List[float]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        } 