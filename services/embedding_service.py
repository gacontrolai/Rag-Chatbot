import os
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import openai

# LangChain imports for embeddings
try:
    from langchain_openai import OpenAIEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class EmbeddingService:
    """Service for creating and managing text embeddings"""
    
    def __init__(self):
        self.local_model = None
        self.openai_embeddings = None
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'sentence-transformers')
        
        # Initialize embedding model based on configuration
        if self.embedding_model == 'openai' and LANGCHAIN_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_embeddings = OpenAIEmbeddings(
                    openai_api_key=os.getenv('OPENAI_API_KEY'),
                    model=os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-ada-002')
                )
                print("OpenAI embeddings initialized successfully")
            except Exception as e:
                print(f"Failed to initialize OpenAI embeddings: {e}")
                self._fallback_to_local()
        else:
            self._fallback_to_local()
    
    def _fallback_to_local(self):
        """Initialize local sentence-transformers model as fallback"""
        try:
            model_name = os.getenv('LOCAL_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
            self.local_model = SentenceTransformer(model_name)
            print(f"Local embedding model '{model_name}' initialized successfully")
        except Exception as e:
            print(f"Failed to initialize local embedding model: {e}")
            self.local_model = None
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts
        Returns: List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            if self.openai_embeddings:
                return self._create_openai_embeddings(texts)
            elif self.local_model:
                return self._create_local_embeddings(texts)
            else:
                raise Exception("No embedding model available")
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            # Return empty embeddings as fallback
            return [[] for _ in texts]
    
    def _create_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using OpenAI API"""
        try:
            embeddings = self.openai_embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            print(f"OpenAI embedding error: {e}")
            # Fallback to local model if available
            if self.local_model:
                return self._create_local_embeddings(texts)
            raise e
    
    def _create_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using local sentence-transformers model"""
        try:
            embeddings = self.local_model.encode(texts, convert_to_tensor=False)
            # Convert numpy arrays to lists for JSON serialization
            return [embedding.tolist() if hasattr(embedding, 'tolist') else embedding 
                   for embedding in embeddings]
        except Exception as e:
            print(f"Local embedding error: {e}")
            raise e
    
    def create_single_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        if not text.strip():
            return []
        
        embeddings = self.create_embeddings([text])
        return embeddings[0] if embeddings else []
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by current model"""
        if self.openai_embeddings:
            # OpenAI text-embedding-ada-002 produces 1536-dimensional embeddings
            return 1536
        elif self.local_model:
            # Get dimension from the model
            return self.local_model.get_sentence_embedding_dimension()
        else:
            return 0
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[Dict[str, Any]], 
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find most similar embeddings to a query embedding
        candidate_embeddings: List of dicts with 'embedding' and other metadata
        Returns: List of candidate dicts sorted by similarity (highest first)
        """
        if not query_embedding or not candidate_embeddings:
            return []
        
        # Calculate similarities
        similarities = []
        for candidate in candidate_embeddings:
            if 'embedding' not in candidate:
                continue
                
            similarity = self.calculate_similarity(query_embedding, candidate['embedding'])
            candidate_with_similarity = candidate.copy()
            candidate_with_similarity['similarity'] = similarity
            similarities.append(candidate_with_similarity)
        
        # Sort by similarity (highest first) and return top_k
        similarities.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        return similarities[:top_k]
    
    def is_available(self) -> bool:
        """Check if embedding service is available"""
        return self.openai_embeddings is not None or self.local_model is not None 