import os
from typing import List, Dict, Any, Tuple
import numpy as np

class RerankerService:
    """Service for reranking retrieved chunks to improve RAG quality"""
    
    def __init__(self):
        self.cross_encoder = None
        self.openai_client = None
        self.reranker_type = os.getenv('RERANKER_TYPE', 'cross-encoder')  # 'cross-encoder', 'openai', 'hybrid'
        
        # Initialize cross-encoder model
        try:
            from sentence_transformers import CrossEncoder
            model_name = os.getenv('CROSS_ENCODER_MODEL', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
            self.cross_encoder = CrossEncoder(model_name)
            print(f"Cross-encoder model loaded: {model_name}")
        except ImportError:
            print("sentence-transformers not available for cross-encoder reranking")
        except Exception as e:
            print(f"Failed to load cross-encoder model: {e}")
        
        # Initialize OpenAI client for reranking
        if os.getenv('OPENAI_API_KEY'):
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                print("OpenAI client initialized for reranking")
            except ImportError:
                print("OpenAI client not available for reranking")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if any reranking method is available"""
        return self.cross_encoder is not None or self.openai_client is not None
    
    def rerank_chunks(self, query: str, chunks: List[Dict[str, Any]], 
                     top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank retrieved chunks based on relevance to query
        
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
            if self.reranker_type == 'cross-encoder' and self.cross_encoder:
                return self._rerank_with_cross_encoder(query, chunks, top_k)
            elif self.reranker_type == 'openai' and self.openai_client:
                return self._rerank_with_openai(query, chunks, top_k)
            elif self.reranker_type == 'hybrid':
                return self._rerank_hybrid(query, chunks, top_k)
            else:
                # Fallback to original order
                return chunks[:top_k]
                
        except Exception as e:
            print(f"Error in reranking: {e}")
            return chunks[:top_k]
    
    def _rerank_with_cross_encoder(self, query: str, chunks: List[Dict[str, Any]], 
                                  top_k: int) -> List[Dict[str, Any]]:
        """Rerank using cross-encoder model"""
        if not self.cross_encoder:
            return chunks[:top_k]
        
        try:
            # Prepare query-document pairs for cross-encoder
            pairs = []
            for chunk in chunks:
                pairs.append([query, chunk['text']])
            
            # Get relevance scores from cross-encoder
            scores = self.cross_encoder.predict(pairs)
            
            # Update chunks with new scores
            reranked_chunks = []
            for i, chunk in enumerate(chunks):
                new_chunk = chunk.copy()
                new_chunk['rerank_score'] = float(scores[i])
                new_chunk['original_score'] = chunk.get('score', 0.0)
                reranked_chunks.append(new_chunk)
            
            # Sort by rerank score (descending)
            reranked_chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            return reranked_chunks[:top_k]
            
        except Exception as e:
            print(f"Error in cross-encoder reranking: {e}")
            return chunks[:top_k]
    
    def _rerank_with_openai(self, query: str, chunks: List[Dict[str, Any]], 
                           top_k: int) -> List[Dict[str, Any]]:
        """Rerank using OpenAI API for relevance scoring"""
        if not self.openai_client:
            return chunks[:top_k]
        
        try:
            # Prepare relevance scoring prompt
            documents_text = ""
            for i, chunk in enumerate(chunks):
                documents_text += f"\nDocument {i+1}: {chunk['text'][:400]}...\n"
            
            prompt = f"""Given this query: "{query}"
            
Rate the relevance of each document on a scale of 0-10 where 10 is most relevant.

Documents:
{documents_text}

Return only a JSON array of scores like: [8.5, 6.2, 9.1, ...]"""

            response = self.openai_client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are a relevance scoring expert. Rate document relevance accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            # Parse scores
            import json
            scores_text = response.choices[0].message.content.strip()
            if scores_text.startswith('[') and scores_text.endswith(']'):
                scores = json.loads(scores_text)
            else:
                # Fallback parsing
                import re
                scores = [float(x) for x in re.findall(r'\d+\.?\d*', scores_text)]
            
            # Update chunks with OpenAI scores
            reranked_chunks = []
            for i, chunk in enumerate(chunks):
                if i < len(scores):
                    new_chunk = chunk.copy()
                    new_chunk['rerank_score'] = scores[i]
                    new_chunk['original_score'] = chunk.get('score', 0.0)
                    reranked_chunks.append(new_chunk)
                else:
                    reranked_chunks.append(chunk)
            
            # Sort by rerank score (descending)
            reranked_chunks.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
            
            return reranked_chunks[:top_k]
            
        except Exception as e:
            print(f"Error in OpenAI reranking: {e}")
            return chunks[:top_k]
    
    def _rerank_hybrid(self, query: str, chunks: List[Dict[str, Any]], 
                      top_k: int) -> List[Dict[str, Any]]:
        """Hybrid reranking combining cross-encoder and original similarity scores"""
        if not self.cross_encoder:
            return chunks[:top_k]
        
        try:
            # Get cross-encoder scores
            cross_encoder_chunks = self._rerank_with_cross_encoder(query, chunks, len(chunks))
            
            # Combine scores: weighted average of original similarity and cross-encoder score
            alpha = 0.7  # Weight for cross-encoder score
            beta = 0.3   # Weight for original similarity score
            
            for chunk in cross_encoder_chunks:
                original_score = chunk.get('original_score', 0.0)
                rerank_score = chunk.get('rerank_score', 0.0)
                
                # Normalize scores to 0-1 range
                normalized_rerank = max(0, min(1, (rerank_score + 1) / 2))  # Cross-encoder scores are typically -1 to 1
                normalized_original = max(0, min(1, original_score))
                
                # Combine scores
                chunk['hybrid_score'] = alpha * normalized_rerank + beta * normalized_original
            
            # Sort by hybrid score
            cross_encoder_chunks.sort(key=lambda x: x['hybrid_score'], reverse=True)
            
            return cross_encoder_chunks[:top_k]
            
        except Exception as e:
            print(f"Error in hybrid reranking: {e}")
            return chunks[:top_k]
    
    def get_reranker_stats(self) -> Dict[str, Any]:
        """Get reranker service statistics"""
        return {
            'reranker_available': self.is_available(),
            'cross_encoder_available': self.cross_encoder is not None,
            'openai_available': self.openai_client is not None,
            'reranker_type': self.reranker_type,
            'cross_encoder_model': os.getenv('CROSS_ENCODER_MODEL', 'cross-encoder/ms-marco-MiniLM-L-6-v2') if self.cross_encoder else None
        }
    
    def calculate_rerank_improvement(self, original_chunks: List[Dict[str, Any]], 
                                   reranked_chunks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate improvement metrics after reranking"""
        if not original_chunks or not reranked_chunks:
            return {}
        
        try:
            # Calculate position changes
            original_order = {chunk.get('chunk_id', i): i for i, chunk in enumerate(original_chunks)}
            position_changes = []
            
            for i, chunk in enumerate(reranked_chunks):
                chunk_id = chunk.get('chunk_id', i)
                if chunk_id in original_order:
                    original_pos = original_order[chunk_id]
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