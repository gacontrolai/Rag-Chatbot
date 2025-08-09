import os
from typing import List, Dict, Any, Tuple
import numpy as np

class RerankerService:
    """Service for reranking retrieved chunks using Pinecone Rerank API"""
    
    def __init__(self):
        self.pinecone_client = None
        self.reranker_model = os.getenv('PINECONE_RERANKER_MODEL', 'bge-reranker-v2-m3')  # 'bge-reranker-v2-m3', 'cohere-rerank-3.5'
        self.reranker_type = os.getenv('RERANKER_TYPE', 'pinecone')  # 'pinecone', 'hybrid', 'disabled'
        
        # Initialize Pinecone client for reranking
        if os.getenv('PINECONE_API_KEY'):
            try:
                from pinecone import Pinecone
                self.pinecone_client = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
                print(f"Pinecone reranker initialized with model: {self.reranker_model}")
            except ImportError:
                print("Pinecone SDK not available for reranking. Install with: pip install pinecone")
            except Exception as e:
                print(f"Failed to initialize Pinecone reranker: {e}")
        else:
            print("PINECONE_API_KEY not found in environment variables")
    
    def is_available(self) -> bool:
        """Check if Pinecone reranking is available"""
        return self.pinecone_client is not None
    
    def rerank_chunks(self, query: str, chunks: List[Dict[str, Any]], 
                     top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank retrieved chunks using Pinecone Rerank API
        
        Args:
            query: Search query
            chunks: List of chunks with 'text', 'score', and other metadata
            top_k: Number of top chunks to return after reranking
            
        Returns:
            Reranked list of chunks with updated scores
        """
        if not chunks or not self.is_available():
            return chunks[:top_k]
        
        try:
            if self.reranker_type == 'pinecone':
                return self._rerank_with_pinecone(query, chunks, top_k)
            elif self.reranker_type == 'hybrid':
                return self._rerank_hybrid(query, chunks, top_k)
            else:
                # Fallback to original order
                return chunks[:top_k]
                
        except Exception as e:
            print(f"Error in reranking: {e}")
            return chunks[:top_k]
    
    def _rerank_with_pinecone(self, query: str, chunks: List[Dict[str, Any]], 
                             top_k: int) -> List[Dict[str, Any]]:
        """Rerank using Pinecone Rerank API"""
        if not self.pinecone_client:
            return chunks[:top_k]
        
        try:
            # Prepare documents for Pinecone Rerank API
            documents = []
            for i, chunk in enumerate(chunks):
                # Pinecone rerank expects documents as strings or dict with 'text' field
                doc_text = chunk.get('text', '')
                if isinstance(doc_text, str) and doc_text.strip():
                    documents.append({
                        "id": str(chunk.get('id', i)),
                        "text": doc_text
                    })
            
            if not documents:
                return chunks[:top_k]
            
            # Call Pinecone Rerank API
            rerank_response = self.pinecone_client.inference.rerank(
                model=self.reranker_model,
                query=query,
                documents=documents,
                top_n=min(top_k, len(documents)),
                return_documents=True
            )
            
            # Map reranked results back to original chunks
            reranked_chunks = []
            doc_id_to_chunk = {}
            
            # Create mapping from document ID to original chunk
            for i, chunk in enumerate(chunks):
                id = str(chunk.get('id', i))
                doc_id_to_chunk[id] = chunk

            # Process reranked results
            for result in rerank_response.data:
                doc_id = result.document.id if hasattr(result.document, 'id') else result.id
                if doc_id in doc_id_to_chunk:
                    original_chunk = doc_id_to_chunk[doc_id].copy()
                    original_chunk['rerank_score'] = float(result.score)
                    original_chunk['original_score'] = doc_id_to_chunk[doc_id].get('score', 0.0)
                    reranked_chunks.append(original_chunk)
                    
            # Sort reranked chunks by rerank_score in descending order
            reranked_chunks.sort(key=lambda x: x['rerank_score'], reverse=True)

            return reranked_chunks[:top_k]
            
        except Exception as e:
            print(f"Error in Pinecone reranking: {e}")
            return chunks[:top_k]
    
    def _rerank_hybrid(self, query: str, chunks: List[Dict[str, Any]], 
                      top_k: int) -> List[Dict[str, Any]]:
        """Hybrid reranking combining Pinecone rerank scores and original similarity scores"""
        if not self.pinecone_client:
            return chunks[:top_k]
        
        try:
            # Get Pinecone rerank scores for all chunks
            pinecone_chunks = self._rerank_with_pinecone(query, chunks, len(chunks))
            
            # Create mapping of chunk IDs to Pinecone scores
            pinecone_scores = {}
            for chunk in pinecone_chunks:
                id = chunk.get('id', str(id(chunk)))
                pinecone_scores[id] = chunk.get('rerank_score', 0.0)
            
            # Combine scores: weighted average of original similarity and Pinecone rerank score
            alpha = 0.7  # Weight for Pinecone rerank score
            beta = 0.3   # Weight for original similarity score
            
            hybrid_chunks = []
            for chunk in chunks:
                id = chunk.get('id', str(id(chunk)))
                original_score = chunk.get('score', 0.0)
                pinecone_score = pinecone_scores.get(id, 0.0)
                
                # Normalize scores to 0-1 range
                normalized_pinecone = max(0, min(1, pinecone_score))  # Pinecone scores are typically 0-1
                normalized_original = max(0, min(1, original_score))
                
                # Create new chunk with combined score
                new_chunk = chunk.copy()
                new_chunk['hybrid_score'] = alpha * normalized_pinecone + beta * normalized_original
                new_chunk['rerank_score'] = pinecone_score
                new_chunk['original_score'] = original_score
                hybrid_chunks.append(new_chunk)
            
            # Sort by hybrid score
            hybrid_chunks.sort(key=lambda x: x['hybrid_score'], reverse=True)
            
            return hybrid_chunks[:top_k]
            
        except Exception as e:
            print(f"Error in hybrid reranking: {e}")
            return chunks[:top_k]
    
    def get_reranker_stats(self) -> Dict[str, Any]:
        """Get reranker service statistics"""
        return {
            'reranker_available': self.is_available(),
            'pinecone_available': self.pinecone_client is not None,
            'reranker_type': self.reranker_type,
            'reranker_model': self.reranker_model if self.pinecone_client else None,
            'supported_models': ['bge-reranker-v2-m3', 'cohere-rerank-3.5']
        }
    
    def calculate_rerank_improvement(self, original_chunks: List[Dict[str, Any]], 
                                   reranked_chunks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate improvement metrics after reranking"""
        if not original_chunks or not reranked_chunks:
            return {}
        
        try:
            # Calculate position changes
            original_order = {chunk.get('id', i): i for i, chunk in enumerate(original_chunks)}
            position_changes = []
            
            for i, chunk in enumerate(reranked_chunks):
                id = chunk.get('id', i)
                if id in original_order:
                    original_pos = original_order[id]
                    position_change = original_pos - i  # Positive means moved up
                    position_changes.append(position_change)
            
            avg_position_change = np.mean(position_changes) if position_changes else 0
            
            # Calculate score improvements
            score_improvements = []
            for chunk in reranked_chunks:
                original_score = chunk.get('original_score', 0)
                rerank_score = chunk.get('rerank_score', 0)
                if original_score > 0:
                    improvement = (rerank_score - original_score) / original_score
                    score_improvements.append(improvement)
            
            avg_score_improvement = np.mean(score_improvements) if score_improvements else 0
            
            return {
                'avg_position_change': float(avg_position_change),
                'avg_score_improvement': float(avg_score_improvement),
                'total_reranked': len(reranked_chunks),
                'reranking_applied': True
            }
            
        except Exception as e:
            print(f"Error calculating rerank improvement: {e}")
            return {'reranking_applied': False}
    
    def set_model(self, model_name: str) -> bool:
        """
        Change the reranker model
        
        Args:
            model_name: Name of the Pinecone reranker model
            
        Returns:
            True if model was set successfully
        """
        supported_models = ['bge-reranker-v2-m3', 'cohere-rerank-3.5']
        if model_name in supported_models:
            self.reranker_model = model_name
            print(f"Reranker model changed to: {model_name}")
            return True
        else:
            print(f"Unsupported model: {model_name}. Supported models: {supported_models}")
            return False 