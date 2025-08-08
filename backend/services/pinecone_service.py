import os
import time
from typing import List, Dict, Any, Optional
from pinecone import Pinecone
from config.settings import Config

class PineconeService:
    """Service for managing Pinecone vector database operations"""
    
    def __init__(self):
        self.api_key = os.getenv('PINECONE_API_KEY')
        self.environment = os.getenv('PINECONE_ENVIRONMENT', 'us-east1-gcp')
        self.index_name = os.getenv('PINECONE_INDEX_NAME', 'rag-chatbot')
        self.index = None
        self.initialized = False
        
        if self.api_key:
            self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and index"""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(
                api_key=self.api_key
            )
            
            # Check if index exists, create if not
            if not self.pc.has_index(self.index_name):
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index_for_model(
                    name=self.index_name,
                    cloud="aws",
                    region="us-east-1",
                    embed={
                        "model":"llama-text-embed-v2",
                        "field_map":{"text": "chunk_text"}
                    }
                )
                # Wait for index to be ready
                time.sleep(60)
            
            # Connect to the index
            self.index = self.pc.Index(self.index_name)
            self.initialized = True
            print(f"Pinecone initialized successfully with index: {self.index_name}")
            
        except Exception as e:
            print(f"Failed to initialize Pinecone: {e}")
            self.initialized = False
    
    def is_available(self) -> bool:
        """Check if Pinecone service is available"""
        return self.initialized and self.index is not None
    
    def upsert_embeddings(self, embeddings_data: List[Dict[str, Any]]) -> bool:
        """
        Upsert embeddings to Pinecone
        embeddings_data: List of dicts with keys: id, values, metadata
        """
        if not self.is_available():
            print("Pinecone service not available")
            return False
        
        try:
            # Prepare vectors for upsert
            vectors = []
            for data in embeddings_data:
                vector = {
                    'id': data['id'],
                    'values': data['embedding'],
                    'metadata': {
                        'workspace_id': data.get('workspace_id'),
                        'file_id': data.get('file_id'),
                        'filename': data.get('filename'),
                        'chunk_id': data.get('chunk_id'),
                        'text': data.get('text', '')[:40000],  # Pinecone metadata limit
                        'start_pos': data.get('start_pos', 0),
                        'end_pos': data.get('end_pos', 0),
                        'char_count': data.get('char_count', 0)
                    }
                }
                vectors.append(vector)
            
            # Upsert in batches (Pinecone recommends batch size of 100)
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            print(f"Successfully upserted {len(vectors)} vectors to Pinecone")
            return True
            
        except Exception as e:
            print(f"Error upserting to Pinecone: {e}")
            return False
    
    def query_embeddings(self, query_embedding: List[float], workspace_id: str, 
                        top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query Pinecone for similar embeddings
        """
        if not self.is_available():
            print("Pinecone service not available")
            return []
        
        try:
            # Query with workspace filter
            response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter={
                    'workspace_id': workspace_id
                }
            )
            
            # Format results
            results = []
            for match in response.matches:
                result = {
                    'id': match.id,
                    'similarity': float(match.score),
                    'file_id': match.metadata.get('file_id'),
                    'filename': match.metadata.get('filename'),
                    'chunk_id': match.metadata.get('chunk_id'),
                    'text': match.metadata.get('text', ''),
                    'start_pos': match.metadata.get('start_pos', 0),
                    'end_pos': match.metadata.get('end_pos', 0)
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            return []
    
    def delete_embeddings(self, ids: List[str]) -> bool:
        """Delete embeddings by IDs"""
        if not self.is_available():
            print("Pinecone service not available")
            return False
        
        try:
            self.index.delete(ids=ids)
            print(f"Successfully deleted {len(ids)} vectors from Pinecone")
            return True
        except Exception as e:
            print(f"Error deleting from Pinecone: {e}")
            return False
    
    def delete_by_workspace(self, workspace_id: str) -> bool:
        """Delete all embeddings for a workspace"""
        if not self.is_available():
            print("Pinecone service not available")
            return False
        
        try:
            self.index.delete(
                filter={
                    'workspace_id': workspace_id
                }
            )
            print(f"Successfully deleted all vectors for workspace: {workspace_id}")
            return True
        except Exception as e:
            print(f"Error deleting workspace vectors from Pinecone: {e}")
            return False
    
    def delete_by_file(self, file_id: str) -> bool:
        """Delete all embeddings for a file"""
        if not self.is_available():
            print("Pinecone service not available")
            return False
        
        try:
            self.index.delete(
                filter={
                    'file_id': file_id
                }
            )
            print(f"Successfully deleted all vectors for file: {file_id}")
            return True
        except Exception as e:
            print(f"Error deleting file vectors from Pinecone: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        if not self.is_available():
            return {'available': False}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                'available': True,
                'total_vector_count': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': stats.namespaces
            }
        except Exception as e:
            print(f"Error getting Pinecone stats: {e}")
            return {'available': False, 'error': str(e)}
    
    def create_chunk_id(self, workspace_id: str, file_id: str, chunk_id: str) -> str:
        """Create a unique ID for Pinecone vector"""
        return f"{workspace_id}_{file_id}_{chunk_id}" 