from typing import List, Dict, Any, Optional
import os
from repositories.file_repo import FileRepository
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService
from services.reranker_service import RerankerService

class RAGService:
    """Service for Retrieval Augmented Generation (RAG) pipeline"""
    
    def __init__(self):
        self.file_repo = FileRepository()
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.reranker_service = RerankerService()
        
        # Load configuration
        self.retrieval_multiplier = int(os.getenv('RERANKER_RETRIEVAL_MULTIPLIER', '2'))
        self.max_candidates = int(os.getenv('RERANKER_MAX_CANDIDATES', '20'))
    
    def search_context(self, workspace_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant context chunks in workspace files with reranking
        Returns list of text chunks with similarity scores
        """
        if not query.strip():
            return []
        
        try:
            # First stage: Retrieve more candidates for reranking using config values
            retrieval_k = min(max(top_k * self.retrieval_multiplier, 10), self.max_candidates)
            
            if self.embedding_service.is_available():
                initial_results = self._semantic_search(workspace_id, query, retrieval_k)
            else:
                initial_results = self._text_search(workspace_id, query, retrieval_k)
            
            # Second stage: Rerank the retrieved candidates
            if len(initial_results) > top_k and self.reranker_service.is_available():
                reranked_results = self.reranker_service.rerank_chunks(
                    query=query,
                    chunks=initial_results,
                    top_k=top_k
                )
                
                # Add reranking metadata
                for chunk in reranked_results:
                    chunk['reranked'] = True
                
                return reranked_results
            else:
                # No reranking needed or available
                for chunk in initial_results[:top_k]:
                    chunk['reranked'] = False
                return initial_results[:top_k]
                
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
            
            # Use vector service for search
            similar_chunks = self.vector_service.search_similar(
                query_embedding, workspace_id, top_k
            )
            
            # Format results for RAG context
            context_chunks = []
            for chunk in similar_chunks:
                context_chunks.append({
                    'id': chunk.get('id'),
                    "start_pos": chunk.get('start_pos'),
                    "end_pos": chunk.get('end_pos'),
                    'text': chunk['text'],
                    'score': chunk.get('similarity', 0.0),
                    'file_id': chunk.get('file_id'),
                    'filename': chunk.get('filename'),
                    'sequence': chunk.get('sequence'),
                    'search_method': 'semantic'
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
                    'sequence': result.get('sequence'),
                    'search_method': 'text'
                })
            
            return context_chunks
            
        except Exception as e:
            print(f"Error in text search: {e}")
            return []
    
    def search_context_with_rerank_metrics(self, workspace_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Enhanced search with reranking metrics for analysis
        Returns both results and reranking performance data
        """
        if not query.strip():
            return {'results': [], 'metrics': {}}
        
        try:
            # Get initial results using config values
            retrieval_k = min(max(top_k * self.retrieval_multiplier, 10), self.max_candidates)
            if self.embedding_service.is_available():
                initial_results = self._semantic_search(workspace_id, query, retrieval_k)
            else:
                initial_results = self._text_search(workspace_id, query, retrieval_k)
            
            if len(initial_results) <= top_k or not self.reranker_service.is_available():
                return {
                    'results': initial_results[:top_k],
                    'metrics': {'reranking_applied': False, 'retrieval_count': len(initial_results)}
                }
            
            # Apply reranking
            reranked_results = self.reranker_service.rerank_chunks(
                query=query,
                chunks=initial_results,
                top_k=top_k
            )
            
            # Calculate improvement metrics
            improvement_metrics = self.reranker_service.calculate_rerank_improvement(
                initial_results, reranked_results
            )
            
            # Add configuration info to metrics
            improvement_metrics['retrieval_count'] = len(initial_results)
            improvement_metrics['retrieval_k'] = retrieval_k
            improvement_metrics['final_count'] = len(reranked_results)
            
            # Add reranking metadata to results
            for chunk in reranked_results:
                chunk['reranked'] = True
            
            return {
                'results': reranked_results,
                'metrics': improvement_metrics
            }
            
        except Exception as e:
            print(f"Error in enhanced search: {e}")
            return {'results': [], 'metrics': {'error': str(e)}}
    
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
        """Get comprehensive RAG pipeline statistics including reranker"""
        embedding_stats = {
            'embedding_service_available': self.embedding_service.is_available(),
            'embedding_dimension': self.embedding_service.get_embedding_dimension() if self.embedding_service.is_available() else 0,
            'model_type': 'openai' if self.embedding_service.openai_embeddings else 'local' if self.embedding_service.local_model else 'none'
        }
        
        # Add vector service stats
        vector_stats = self.vector_service.get_stats()
        embedding_stats.update(vector_stats)
        
        # Add reranker service stats
        reranker_stats = self.reranker_service.get_reranker_stats()
        embedding_stats['reranker'] = reranker_stats
        
        return embedding_stats
    
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