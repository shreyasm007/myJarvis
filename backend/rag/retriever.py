"""
Document retriever for RAG pipeline.

Handles document retrieval from vector store with
relevance filtering and context formatting.
"""

from typing import List, Optional, Tuple

from backend.config import get_settings
from backend.core.exceptions import RetrievalError
from backend.core.logging_config import get_logger
from backend.rag.embeddings import get_embeddings_client
from backend.rag.vectorstore import get_vectorstore_client

logger = get_logger(__name__)


class Retriever:
    """Retrieves relevant documents for a given query."""
    
    def __init__(self):
        """Initialize the retriever with embedding and vector store clients."""
        self.embeddings_client = get_embeddings_client()
        self.vectorstore_client = get_vectorstore_client()
        
        settings = get_settings()
        self.top_k = settings.rag_top_k
        self.score_threshold = settings.rag_score_threshold
        
        logger.info(
            f"Initialized Retriever with top_k={self.top_k}, "
            f"score_threshold={self.score_threshold}"
        )
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> List[dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User's query string
            top_k: Number of documents to retrieve (optional)
            score_threshold: Minimum similarity score (optional)
            
        Returns:
            List of relevant documents with content, score, and metadata
            
        Raises:
            RetrievalError: If retrieval fails
        """
        try:
            logger.info(f"Retrieving documents for query: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = self.embeddings_client.embed_text(
                text=query,
                input_type="query",
            )
            
            # Search vector store
            results = self.vectorstore_client.search(
                query_embedding=query_embedding,
                top_k=top_k or self.top_k,
                score_threshold=score_threshold or self.score_threshold,
            )
            
            logger.info(f"Retrieved {len(results)} relevant documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {str(e)}")
            raise RetrievalError(
                message="Failed to retrieve documents",
                details={"error": str(e), "query": query[:100]},
            )
    
    def retrieve_with_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> Tuple[str, List[dict]]:
        """
        Retrieve documents and format as context string.
        
        Args:
            query: User's query string
            top_k: Number of documents to retrieve (optional)
            score_threshold: Minimum similarity score (optional)
            
        Returns:
            Tuple of (formatted context string, raw results list)
            
        Raises:
            RetrievalError: If retrieval fails
        """
        results = self.retrieve(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        
        if not results:
            logger.warning("No relevant documents found for query")
            return "", []
        
        # Format results as context
        context_parts = []
        for i, result in enumerate(results, 1):
            content = result["content"]
            score = result["score"]
            metadata = result.get("metadata", {})
            
            # Add source info if available
            source_info = ""
            if "source" in metadata:
                source_info = f" (Source: {metadata['source']})"
            
            context_parts.append(
                f"[Document {i}]{source_info} (Relevance: {score:.2f}):\n{content}"
            )
        
        context = "\n\n---\n\n".join(context_parts)
        
        logger.debug(f"Formatted context with {len(context)} characters")
        return context, results
    
    def has_relevant_documents(
        self,
        query: str,
        score_threshold: Optional[float] = None,
    ) -> bool:
        """
        Check if there are relevant documents for a query.
        
        Args:
            query: User's query string
            score_threshold: Minimum similarity score (optional)
            
        Returns:
            True if relevant documents exist, False otherwise
        """
        try:
            results = self.retrieve(
                query=query,
                top_k=1,
                score_threshold=score_threshold or self.score_threshold,
            )
            return len(results) > 0
        except Exception:
            return False


# Singleton instance
_retriever = None


def get_retriever() -> Retriever:
    """
    Get the singleton retriever instance.
    
    Returns:
        Retriever instance
    """
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
