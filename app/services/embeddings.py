import logging
import numpy as np
from typing import List
from google import genai
from google.genai import types
from app.models.schemas import DocumentChunk
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Handles semantic search using Gemini's native embeddings for maximum accuracy
    """
    
    def __init__(self):
        self.chunks = []
        self.embeddings = []
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini client for embeddings"""
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required for embeddings")
            
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            logger.info("Gemini client initialized for embeddings")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client for embeddings: {str(e)}")
            self.client = None
    
    def _get_embedding(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        """Get embedding using Gemini's native embedding model"""
        try:
            if not self.client:
                raise ValueError("Gemini client not initialized")
            
            response = self.client.models.embed_content(
                model="models/embedding-001",
                content=text,
                task_type=task_type
            )
            
            return response.embedding
            
        except Exception as e:
            logger.error(f"Failed to get embedding: {str(e)}")
            # Fallback to keyword matching if embeddings fail
            return None
    
    def create_vector_index(self, chunks: List[DocumentChunk]) -> None:
        """
        Create vector index using Gemini embeddings for semantic search
        """
        try:
            logger.info(f"Creating semantic index for {len(chunks)} chunks using Gemini embeddings")
            self.chunks = chunks
            self.embeddings = []
            
            # Generate embeddings for each chunk
            for i, chunk in enumerate(chunks):
                try:
                    embedding = self._get_embedding(chunk.content, "retrieval_document")
                    if embedding:
                        # Normalize the embedding vector
                        embedding_array = np.array(embedding)
                        normalized_embedding = embedding_array / np.linalg.norm(embedding_array)
                        self.embeddings.append(normalized_embedding.tolist())
                    else:
                        # Fallback to zero vector if embedding fails
                        self.embeddings.append([0.0] * 768)  # Standard embedding size
                        
                    if (i + 1) % 10 == 0:
                        logger.info(f"Processed {i + 1}/{len(chunks)} chunk embeddings")
                        
                except Exception as e:
                    logger.warning(f"Failed to embed chunk {i}: {str(e)}")
                    # Use zero vector as fallback
                    self.embeddings.append([0.0] * 768)
            
            logger.info(f"Semantic index created with {len(self.embeddings)} embeddings")
            
        except Exception as e:
            logger.error(f"Failed to create semantic index: {str(e)}")
            # Fallback to simple storage for keyword matching
            self.chunks = chunks
            self.embeddings = []
            logger.info("Falling back to keyword-based search")
    
    def search_similar_chunks(self, query: str, top_k: int = 5) -> List[DocumentChunk]:
        """
        Search for similar chunks using Gemini embeddings (semantic search)
        """
        try:
            if not self.chunks:
                raise ValueError("Index not initialized. Create index first.")
            
            logger.info(f"Searching for top {top_k} similar chunks using semantic similarity")
            
            # Try semantic search first
            if self.embeddings and len(self.embeddings) == len(self.chunks):
                try:
                    # Get query embedding
                    query_embedding = self._get_embedding(query, "retrieval_query")
                    
                    if query_embedding:
                        # Normalize query embedding
                        query_array = np.array(query_embedding)
                        query_normalized = query_array / np.linalg.norm(query_array)
                        
                        # Calculate cosine similarities
                        similarities = []
                        for i, chunk_embedding in enumerate(self.embeddings):
                            chunk_array = np.array(chunk_embedding)
                            similarity = np.dot(query_normalized, chunk_array)
                            similarities.append((self.chunks[i], similarity))
                        
                        # Sort by similarity and return top_k
                        similarities.sort(key=lambda x: x[1], reverse=True)
                        similar_chunks = [chunk for chunk, score in similarities[:top_k]]
                        
                        logger.info(f"Found {len(similar_chunks)} semantically similar chunks")
                        return similar_chunks
                
                except Exception as e:
                    logger.warning(f"Semantic search failed: {str(e)}, falling back to keyword search")
            
            # Fallback to keyword matching
            logger.info("Using keyword-based search as fallback")
            query_words = set(query.lower().split())
            scored_chunks = []
            
            for chunk in self.chunks:
                chunk_words = set(chunk.content.lower().split())
                overlap = len(query_words.intersection(chunk_words))
                if overlap > 0:
                    scored_chunks.append((chunk, overlap))
            
            scored_chunks.sort(key=lambda x: x[1], reverse=True)
            similar_chunks = [chunk for chunk, score in scored_chunks[:top_k]]
            
            # Fill remaining slots if needed
            if len(similar_chunks) < top_k:
                used_chunk_ids = {chunk.chunk_id for chunk in similar_chunks}
                for chunk in self.chunks:
                    if chunk.chunk_id not in used_chunk_ids and len(similar_chunks) < top_k:
                        similar_chunks.append(chunk)
            
            logger.info(f"Found {len(similar_chunks)} similar chunks using keyword matching")
            return similar_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to search similar chunks: {str(e)}")
            raise ValueError(f"Failed to search similar chunks: {str(e)}")
    
    def get_context_for_question(self, question: str, top_k: int = 5) -> str:
        """
        Get relevant context for a question by combining similar chunks
        """
        try:
            similar_chunks = self.search_similar_chunks(question, top_k)
            
            if not similar_chunks:
                return "No relevant context found in the document."
            
            # Combine chunk contents
            context_parts = []
            for i, chunk in enumerate(similar_chunks, 1):
                page_info = f"[Page {chunk.page_number}]" if chunk.page_number else "[Unknown Page]"
                context_parts.append(f"{page_info} {chunk.content}")
            
            context = "\n\n".join(context_parts)
            
            logger.info(f"Generated context from {len(similar_chunks)} chunks")
            return context
            
        except Exception as e:
            logger.error(f"Failed to get context for question: {str(e)}")
            raise ValueError(f"Failed to get context for question: {str(e)}")
    
    def clear_index(self):
        """
        Clear the current chunks and embeddings
        """
        self.chunks = []
        self.embeddings = []
        logger.info("Semantic search index cleared")
