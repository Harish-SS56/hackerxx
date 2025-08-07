import logging
from typing import List
from app.models.schemas import DocumentChunk

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Handles text search using simple text matching (simplified for disk space constraints)
    """
    
    def __init__(self):
        self.chunks = []
    
    def create_vector_index(self, chunks: List[DocumentChunk]) -> None:
        """
        Store document chunks for text-based search
        """
        try:
            logger.info(f"Storing {len(chunks)} chunks for text search")
            self.chunks = chunks
            logger.info("Text search index created")
            
        except Exception as e:
            logger.error(f"Failed to create text index: {str(e)}")
            raise ValueError(f"Failed to create text index: {str(e)}")
    
    def search_similar_chunks(self, query: str, top_k: int = 5) -> List[DocumentChunk]:
        """
        Search for similar chunks using keyword matching
        """
        try:
            if not self.chunks:
                raise ValueError("Text index not initialized. Create index first.")
            
            logger.info(f"Searching for top {top_k} similar chunks using keyword matching")
            
            # Simple keyword-based search
            query_words = set(query.lower().split())
            scored_chunks = []
            
            for chunk in self.chunks:
                chunk_words = set(chunk.content.lower().split())
                # Calculate simple overlap score
                overlap = len(query_words.intersection(chunk_words))
                if overlap > 0:
                    scored_chunks.append((chunk, overlap))
            
            # Sort by score and return top_k
            scored_chunks.sort(key=lambda x: x[1], reverse=True)
            similar_chunks = [chunk for chunk, score in scored_chunks[:top_k]]
            
            # If not enough keyword matches, add remaining chunks
            if len(similar_chunks) < top_k:
                used_chunk_ids = {chunk.chunk_id for chunk in similar_chunks}
                for chunk in self.chunks:
                    if chunk.chunk_id not in used_chunk_ids and len(similar_chunks) < top_k:
                        similar_chunks.append(chunk)
            
            logger.info(f"Found {len(similar_chunks)} similar chunks")
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
        Clear the current chunks
        """
        self.chunks = []
        logger.info("Text search index cleared")
