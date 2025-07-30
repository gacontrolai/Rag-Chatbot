from typing import List, Dict, Any, Optional
from repositories.file_repo import FileRepository
from services.embedding_service import EmbeddingService

class RAGService:
    """Service for Retrieval Augmented Generation (RAG) pipeline"""
    
    def __init__(self):
        self.file_repo = FileRepository()
        self.embedding_service = EmbeddingService()
    
    def search_context(self, workspace_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant context chunks in workspace files
        Returns list of text chunks with similarity scores
        """
        if not query.strip():
            return []
        
        try:
            if self.embedding_service.is_available():
                return self._semantic_search(workspace_id, query, top_k)
            else:
                return self._text_search(workspace_id, query, top_k)
        except Exception as e:
            print(f"Error in RAG context search: {e}")
            return []
    
    def _semantic_search(self, workspace_id: str, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform semantic search using embeddings"""
        try:
            # Create embedding for search query
            query_embedding = self.embedding_service.create_single_embedding(query)
            
            if not query_embedding:
                return self._text_search(workspace_id, query, top_k)
            
            # Get all file chunks with embeddings from workspace
            file_chunks = self.file_repo.get_chunks_with_embeddings(workspace_id)
            
            if not file_chunks:
                return []
            
            # Find most similar chunks
            similar_chunks = self.embedding_service.find_most_similar(
                query_embedding, file_chunks, top_k
            )
            
            # Format results for RAG context
            context_chunks = []
            for chunk in similar_chunks:
                context_chunks.append({
                    'text': chunk['text'],
                    'score': chunk.get('similarity', 0.0),
                    'file_id': chunk.get('file_id'),
                    'filename': chunk.get('filename'),
                    'chunk_id': chunk.get('chunk_id')
                })
            
            return context_chunks
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return self._text_search(workspace_id, query, top_k)
    
    def _text_search(self, workspace_id: str, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback text-based search"""
        try:
            results = self.file_repo.search_text_chunks(workspace_id, query, top_k)
            
            # Format results for RAG context
            context_chunks = []
            for result in results:
                context_chunks.append({
                    'text': result['text'],
                    'score': result.get('similarity', 0.5),
                    'file_id': result.get('file_id'),
                    'filename': result.get('filename'),
                    'chunk_id': result.get('chunk_id')
                })
            
            return context_chunks
            
        except Exception as e:
            print(f"Error in text search: {e}")
            return []
    
    def embed_text(self, text: str) -> List[float]:
        """
        Create embedding for text (placeholder implementation)
        In production, this would use OpenAI embeddings or similar
        """
        if self.embedding_service.is_available():
            return self.embedding_service.create_single_embedding(text)
        else:
            print("Embedding service not available")
            return []
    
    def process_document_chunks(self, document_text: str, file_id: str) -> List[Dict[str, Any]]:
        """
        Process document text into chunks with embeddings
        This is now handled by ContentExtractor and EmbeddingService
        """
        # This method is kept for backwards compatibility
        # Actual processing is now done in FileService.upload_file()
        print("process_document_chunks is deprecated. Use FileService.upload_file() instead.")
        return []
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding service statistics"""
        return {
            'embedding_service_available': self.embedding_service.is_available(),
            'embedding_dimension': self.embedding_service.get_embedding_dimension() if self.embedding_service.is_available() else 0,
            'model_type': 'openai' if self.embedding_service.openai_embeddings else 'local' if self.embedding_service.local_model else 'none'
        }
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not self.embedding_service.is_available():
            return 0.0
        
        try:
            embedding1 = self.embedding_service.create_single_embedding(text1)
            embedding2 = self.embedding_service.create_single_embedding(text2)
            
            if embedding1 and embedding2:
                return self.embedding_service.calculate_similarity(embedding1, embedding2)
            else:
                return 0.0
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0 