import os
from typing import List, Dict, Any, Optional
from services.pinecone_service import PineconeService
from repositories.file_repo import FileRepository

class VectorService:
    """Unified service for vector storage operations (Pinecone or MongoDB)"""
    
    def __init__(self):
        self.vector_store = os.getenv('VECTOR_STORE', 'pinecone').lower()
        self.pinecone_service = None
        self.file_repo = None
        
        if self.vector_store == 'pinecone':
            self.pinecone_service = PineconeService()
            if not self.pinecone_service.is_available():
                print("Pinecone not available, falling back to MongoDB")
                self.vector_store = 'mongodb'
                self.file_repo = FileRepository()
        else:
            self.file_repo = FileRepository()
    
    def is_available(self) -> bool:
        """Check if vector service is available"""
        if self.vector_store == 'pinecone':
            return self.pinecone_service and self.pinecone_service.is_available()
        else:
            return self.file_repo is not None
    
    def store_embeddings(self, workspace_id: str, file_id: str, 
                        text_chunks: List[Dict[str, Any]]) -> bool:
        """Store embeddings in the configured vector store"""
        if not self.is_available():
            return False
        
        try:
            if self.vector_store == 'pinecone':
                return self._store_in_pinecone(workspace_id, file_id, text_chunks)
            else:
                return self._store_in_mongodb(file_id, text_chunks)
        except Exception as e:
            print(f"Error storing embeddings: {e}")
            return False
    
    def _store_in_pinecone(self, workspace_id: str, file_id: str, 
                          text_chunks: List[Dict[str, Any]]) -> bool:
        """Store embeddings in Pinecone"""
        embeddings_data = []
        
        for chunk in text_chunks:
            if not chunk.get('embedding'):
                continue
                
            pinecone_id = self.pinecone_service.create_chunk_id(
                workspace_id, file_id, str(chunk['chunk_id'])
            )
            
            embedding_data = {
                'id': pinecone_id,
                'embedding': chunk['embedding'],
                'workspace_id': workspace_id,
                'file_id': file_id,
                'filename': chunk.get('filename', ''),
                'chunk_id': str(chunk['chunk_id']),
                'text': chunk['text'],
                'start_pos': chunk.get('start_pos', 0),
                'end_pos': chunk.get('end_pos', 0),
                'char_count': chunk.get('char_count', 0)
            }
            embeddings_data.append(embedding_data)
        
        if embeddings_data:
            return self.pinecone_service.upsert_embeddings(embeddings_data)
        return True
    
    def _store_in_mongodb(self, file_id: str, text_chunks: List[Dict[str, Any]]) -> bool:
        """Store embeddings in MongoDB (existing method)"""
        return self.file_repo.add_text_chunks(file_id, text_chunks)
    
    def search_similar(self, query_embedding: List[float], workspace_id: str, 
                      top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        if not self.is_available():
            return []
        
        try:
            if self.vector_store == 'pinecone':
                return self._search_in_pinecone(query_embedding, workspace_id, top_k)
            else:
                return self._search_in_mongodb(query_embedding, workspace_id, top_k)
        except Exception as e:
            print(f"Error searching embeddings: {e}")
            return []
    
    def _search_in_pinecone(self, query_embedding: List[float], workspace_id: str, 
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """Search embeddings in Pinecone"""
        return self.pinecone_service.query_embeddings(query_embedding, workspace_id, top_k)
    
    def _search_in_mongodb(self, query_embedding: List[float], workspace_id: str, 
                          top_k: int = 5) -> List[Dict[str, Any]]:
        """Search embeddings in MongoDB (using existing method)"""
        # Get all chunks with embeddings
        file_chunks = self.file_repo.get_chunks_with_embeddings(workspace_id)
        
        if not file_chunks:
            return []
        
        # Calculate similarities (this was previously done in embedding_service)
        from services.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        
        return embedding_service.find_most_similar(query_embedding, file_chunks, top_k)
    
    def delete_embeddings_by_file(self, file_id: str, workspace_id: str = None) -> bool:
        """Delete all embeddings for a file"""
        if not self.is_available():
            return False
        
        try:
            if self.vector_store == 'pinecone':
                return self.pinecone_service.delete_by_file(file_id)
            else:
                # For MongoDB, embeddings are deleted when file is deleted
                return True
        except Exception as e:
            print(f"Error deleting file embeddings: {e}")
            return False
    
    def delete_embeddings_by_workspace(self, workspace_id: str) -> bool:
        """Delete all embeddings for a workspace"""
        if not self.is_available():
            return False
        
        try:
            if self.vector_store == 'pinecone':
                return self.pinecone_service.delete_by_workspace(workspace_id)
            else:
                # For MongoDB, embeddings are deleted when files are deleted
                return True
        except Exception as e:
            print(f"Error deleting workspace embeddings: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        stats = {
            'vector_store': self.vector_store,
            'available': self.is_available()
        }
        
        try:
            if self.vector_store == 'pinecone' and self.pinecone_service:
                pinecone_stats = self.pinecone_service.get_index_stats()
                stats.update(pinecone_stats)
            else:
                stats['storage'] = 'mongodb'
                
        except Exception as e:
            stats['error'] = str(e)
        
        return stats 