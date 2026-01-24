"""
RAG chain orchestrator.

Coordinates the complete RAG pipeline: query embedding,
document retrieval, context building, and LLM response generation.
"""

from typing import Any, Dict, Generator, List, Optional, Tuple
from uuid import uuid4

from backend.api.schemas import Source
from backend.core.exceptions import RAGException
from backend.core.logging_config import get_logger
from backend.rag.embeddings import EmbeddingsClient
from backend.rag.llm import LLMClient, get_llm_client
from backend.rag.prompts import build_messages, get_fallback_response
from backend.rag.retriever import Retriever, get_retriever

logger = get_logger(__name__)


class RAGChain:
    """Orchestrates the complete RAG pipeline."""
    
    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        llm_client: Optional[LLMClient] = None,
        embeddings_client: Optional[EmbeddingsClient] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize the RAG chain with retriever and LLM client.
        
        Args:
            retriever: Optional custom retriever instance
            llm_client: Optional custom LLM client instance
            embeddings_client: Optional embeddings client (for custom retriever)
            model_name: Optional custom model name
            temperature: LLM temperature setting
        """
        self.retriever = retriever or get_retriever()
        self.llm_client = llm_client or get_llm_client(model_name=model_name, temperature=temperature)
        
        logger.info("Initialized RAGChain")
    
    def process_query(
        self,
        query: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline.
        
        Args:
            query: User's question
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            Dictionary with response, conversation_id, sources, and contexts
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid4())
        
        logger.info(
            f"Processing query (conversation_id={conversation_id}): {query[:100]}..."
        )
        
        try:
            # Retrieve relevant context
            context, raw_results = self.retriever.retrieve_with_context(query)
            
            # Check if we have relevant context
            if not context:
                logger.info("No relevant context found, returning fallback")
                return {
                    "response": get_fallback_response("no_context"),
                    "conversation_id": conversation_id,
                    "sources": [],
                    "contexts": [],
                }
            
            # Build messages for LLM
            messages = build_messages(context=context, question=query)
            
            # Generate response
            response = self.llm_client.generate(messages)
            
            # Build source list
            sources = [
                Source(
                    content=result["content"][:500],  # Truncate for response
                    score=result["score"],
                    metadata=result.get("metadata"),
                )
                for result in raw_results
            ]
            
            logger.info(
                f"Generated response for conversation {conversation_id} "
                f"with {len(sources)} sources"
            )
            
            return {
                "response": response,
                "conversation_id": conversation_id,
                "sources": sources,
                "contexts": raw_results,  # Full contexts for debugging
            }
            
        except RAGException as e:
            logger.error(f"RAG pipeline error: {e.message}", extra=e.details)
            return {
                "response": get_fallback_response("error"),
                "conversation_id": conversation_id,
                "sources": [],
                "contexts": [],
            }
        except Exception as e:
            logger.error(f"Unexpected error in RAG pipeline: {str(e)}")
            return {
                "response": get_fallback_response("error"),
                "conversation_id": conversation_id,
                "sources": [],
                "contexts": [],
            }
    
    def process_query_stream(
        self,
        query: str,
        conversation_id: Optional[str] = None,
    ) -> Generator[Tuple[str, bool, Optional[str], List[Source]], None, None]:
        """
        Process a user query with streaming response.
        
        Args:
            query: User's question
            conversation_id: Optional conversation ID for tracking
            
        Yields:
            Tuples of (chunk, is_final, conversation_id, sources)
            - chunk: Response text chunk
            - is_final: Whether this is the final chunk
            - conversation_id: Included in final chunk
            - sources: Included in final chunk
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid4())
        
        logger.info(
            f"Processing streaming query (conversation_id={conversation_id}): "
            f"{query[:100]}..."
        )
        
        try:
            # Retrieve relevant context
            context, raw_results = self.retriever.retrieve_with_context(query)
            
            # Check if we have relevant context
            if not context:
                logger.info("No relevant context found, returning fallback")
                fallback = get_fallback_response("no_context")
                yield (fallback, True, conversation_id, [])
                return
            
            # Build messages for LLM
            messages = build_messages(context=context, question=query)
            
            # Build source list
            sources = [
                Source(
                    content=result["content"][:500],
                    score=result["score"],
                    metadata=result.get("metadata"),
                )
                for result in raw_results
            ]
            
            # Stream response
            full_response = ""
            for chunk in self.llm_client.generate_stream(messages):
                full_response += chunk
                yield (chunk, False, None, [])
            
            # Final chunk with metadata
            yield ("", True, conversation_id, sources)
            
            logger.info(
                f"Completed streaming response for conversation {conversation_id}"
            )
            
        except RAGException as e:
            logger.error(f"RAG pipeline error: {e.message}", extra=e.details)
            yield (get_fallback_response("error"), True, conversation_id, [])
            
        except Exception as e:
            logger.error(f"Unexpected error in RAG pipeline: {str(e)}")
            yield (get_fallback_response("error"), True, conversation_id, [])


# Singleton instance
_rag_chain = None


def get_rag_chain() -> RAGChain:
    """
    Get the singleton RAG chain instance.
    
    Returns:
        RAGChain instance
    """
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = RAGChain()
    return _rag_chain
