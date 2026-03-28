"""
Voyage AI embeddings client.

Handles text embedding generation using Voyage AI API with Redis caching.
"""

import hashlib
import json
from typing import List, Optional

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

import voyageai

from backend.config import get_settings
from backend.core.exceptions import EmbeddingError
from backend.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingsClient:
    """Client for generating embeddings using Voyage AI with Redis caching."""
    
    def __init__(self, use_cache: bool = True, redis_url: Optional[str] = None):
        """Initialize the Voyage AI client with optional Redis cache.
        
        Args:
            use_cache: Enable Redis caching (default: True)
            redis_url: Redis connection URL (default: localhost:6379)
        """
        settings = get_settings()
        self.client = voyageai.Client(api_key=settings.voyage_api_key)
        self.model = settings.voyage_model
        self.use_cache = use_cache
        
        # Initialize Redis cache
        if use_cache and HAS_REDIS:
            try:
                redis_url = redis_url or "redis://localhost:6379/0"
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=False,  # Store binary data
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                # Test connection
                self.redis_client.ping()
                logger.info(f"Initialized EmbeddingsClient with model: {self.model} (Redis cache enabled)")
            except Exception as e:
                logger.warning(f"Redis cache unavailable, falling back to no cache: {e}")
                self.use_cache = False
                self.redis_client = None
        else:
            self.redis_client = None
            logger.info(f"Initialized EmbeddingsClient with model: {self.model} (cache disabled)")
    
    def _get_cache_key(self, text: str, input_type: str) -> str:
        """Generate cache key for text embedding."""
        content = f"{self.model}:{input_type}:{text}"
        return f"emb:{hashlib.sha256(content.encode()).hexdigest()}"
    
    def embed_text(self, text: str, input_type: str = "query") -> List[float]:
        """
        Generate embedding for a single text with Redis caching.
        
        Args:
            text: Text to embed
            input_type: Type of input ("query" or "document")
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        # Check cache first
        if self.use_cache and self.redis_client:
            try:
                cache_key = self._get_cache_key(text, input_type)
                cached = self.redis_client.get(cache_key)
                if cached:
                    embedding = json.loads(cached)
                    logger.debug(f"Cache hit for embedding (type={input_type})")
                    return embedding
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
        
        try:
            logger.debug(f"Generating embedding for text (type={input_type}): {text[:100]}...")
            
            result = self.client.embed(
                texts=[text],
                model=self.model,
                input_type=input_type,
            )
            
            embedding = result.embeddings[0]
            logger.debug(f"Generated embedding with dimension: {len(embedding)}")
            
            # Cache the result (TTL: 7 days for queries, 30 days for documents)
            if self.use_cache and self.redis_client:
                try:
                    cache_key = self._get_cache_key(text, input_type)
                    ttl = 604800 if input_type == "query" else 2592000  # 7d or 30d
                    self.redis_client.setex(
                        cache_key,
                        ttl,
                        json.dumps(embedding)
                    )
                except Exception as e:
                    logger.warning(f"Cache write failed: {e}")
            
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
