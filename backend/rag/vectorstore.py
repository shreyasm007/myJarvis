"""
Qdrant vector store client.

Handles all vector database operations including
storing, searching, and managing document embeddings.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse

from backend.config import get_settings
from backend.core.exceptions import VectorStoreError
from backend.core.logging_config import get_logger

logger = get_logger(__name__)


class VectorStoreClient:
    """Client for Qdrant vector database operations."""
    
    def __init__(self):
        """Initialize the Qdrant client."""
        settings = get_settings()
        
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name
        
        logger.info(
            f"Initialized VectorStoreClient for collection: {self.collection_name}"
        )
    
    def ensure_collection_exists(self, vector_size: int) -> bool:
        """
        Ensure the collection exists, creating it if necessary.
        
        Args:
            vector_size: Dimension of the embedding vectors
            
        Returns:
            True if collection exists or was created
            
        Raises:
            VectorStoreError: If collection creation fails
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
            
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=vector_size,
                    distance=qdrant_models.Distance.COSINE,
                ),
            )
            
            logger.info(
                f"Created collection '{self.collection_name}' with vector size {vector_size}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            raise VectorStoreError(
                message="Failed to ensure collection exists",
                details={"error": str(e), "collection": self.collection_name},
            )
    
    def upsert_documents(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> int:
        """
        Insert or update documents in the vector store.
        
        Args:
            embeddings: List of embedding vectors
            documents: List of document texts
            metadata_list: Optional list of metadata dicts for each document
            ids: Optional list of IDs (generated if not provided)
            
        Returns:
            Number of documents upserted
            
        Raises:
            VectorStoreError: If upsert operation fails
        """
        if not embeddings or not documents:
            logger.warning("Empty embeddings or documents provided for upsert")
            return 0
        
        if len(embeddings) != len(documents):
            raise VectorStoreError(
                message="Embeddings and documents count mismatch",
                details={
                    "embeddings_count": len(embeddings),
                    "documents_count": len(documents),
                },
            )
        
        try:
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid4()) for _ in range(len(documents))]
            
            # Prepare metadata
            if metadata_list is None:
                metadata_list = [{} for _ in range(len(documents))]
            
            # Create points
            points = []
            for i, (embedding, doc, metadata, doc_id) in enumerate(
                zip(embeddings, documents, metadata_list, ids)
            ):
                payload = {
                    "content": doc,
                    **metadata,
                }
                points.append(
                    qdrant_models.PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload=payload,
                    )
                )
            
            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            
            logger.info(f"Successfully upserted {len(points)} documents")
            return len(points)
            
        except Exception as e:
            logger.error(f"Failed to upsert documents: {str(e)}")
            raise VectorStoreError(
                message="Failed to upsert documents",
                details={"error": str(e), "document_count": len(documents)},
            )
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score (optional)
            
        Returns:
            List of search results with content, score, and metadata
            
        Raises:
            VectorStoreError: If search operation fails
        """
        try:
            logger.debug(f"Searching for top {top_k} similar documents")
            
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
            ).points
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.payload.get("content", ""),
                    "score": result.score,
                    "metadata": {
                        k: v for k, v in result.payload.items() if k != "content"
                    },
                    "id": result.id,
                })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {str(e)}")
            raise VectorStoreError(
                message="Failed to search documents",
                details={"error": str(e)},
            )
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection statistics
            
        Raises:
            VectorStoreError: If operation fails
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count if hasattr(info, 'vectors_count') else info.points_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except UnexpectedResponse as e:
            if "404" in str(e) or "Not found" in str(e):
                return {
                    "name": self.collection_name,
                    "vectors_count": 0,
                    "points_count": 0,
                    "status": "not_found",
                }
            raise VectorStoreError(
                message="Failed to get collection info",
                details={"error": str(e)},
            )
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            raise VectorStoreError(
                message="Failed to get collection info",
                details={"error": str(e)},
            )
    
    def delete_collection(self) -> bool:
        """
        Delete the collection.
        
        Returns:
            True if deletion was successful
            
        Raises:
            VectorStoreError: If deletion fails
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            raise VectorStoreError(
                message="Failed to delete collection",
                details={"error": str(e)},
            )


# Singleton instance
_vectorstore_client = None


def get_vectorstore_client() -> VectorStoreClient:
    """
    Get the singleton vector store client instance.
    
    Returns:
        VectorStoreClient instance
    """
    global _vectorstore_client
    if _vectorstore_client is None:
        _vectorstore_client = VectorStoreClient()
    return _vectorstore_client
