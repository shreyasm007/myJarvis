"""
Voyage AI embeddings client.

Handles text embedding generation using Voyage AI API.
"""

from typing import List

import voyageai

from backend.config import get_settings
from backend.core.exceptions import EmbeddingError
from backend.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingsClient:
    """Client for generating embeddings using Voyage AI."""
    
    def __init__(self):
        """Initialize the Voyage AI client."""
        settings = get_settings()
        self.client = voyageai.Client(api_key=settings.voyage_api_key)
        self.model = settings.voyage_model
        logger.info(f"Initialized EmbeddingsClient with model: {self.model}")
    
    def embed_text(self, text: str, input_type: str = "query") -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            input_type: Type of input ("query" or "document")
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            logger.debug(f"Generating embedding for text (type={input_type}): {text[:100]}...")
            
            result = self.client.embed(
                texts=[text],
                model=self.model,
                input_type=input_type,
            )
            
            embedding = result.embeddings[0]
            logger.debug(f"Generated embedding with dimension: {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise EmbeddingError(
                message="Failed to generate embedding",
                details={"error": str(e), "text_preview": text[:100]},
            )
    
    def embed_texts(self, texts: List[str], input_type: str = "document") -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            input_type: Type of input ("query" or "document")
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not texts:
            logger.warning("Empty text list provided for embedding")
            return []
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts (type={input_type})")
            
            result = self.client.embed(
                texts=texts,
                model=self.model,
                input_type=input_type,
            )
            
            embeddings = result.embeddings
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise EmbeddingError(
                message="Failed to generate embeddings",
                details={"error": str(e), "text_count": len(texts)},
            )
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by the model.
        
        Returns:
            Embedding dimension size
        """
        # Generate a test embedding to get dimension
        test_embedding = self.embed_text("test", input_type="query")
        return len(test_embedding)


# Singleton instance
_embeddings_client = None


def get_embeddings_client() -> EmbeddingsClient:
    """
    Get the singleton embeddings client instance.
    
    Returns:
        EmbeddingsClient instance
    """
    global _embeddings_client
    if _embeddings_client is None:
        _embeddings_client = EmbeddingsClient()
    return _embeddings_client
