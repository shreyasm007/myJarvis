"""
Conversation logging service.

Logs all conversations (questions and answers) for analytics
and debugging purposes.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.core.logging_config import get_conversation_logger, get_logger

logger = get_logger(__name__)
conversation_logger = get_conversation_logger()


class ConversationLogger:
    """Service for logging conversations."""
    
    def __init__(self):
        """Initialize the conversation logger."""
        logger.info("Initialized ConversationLogger")
    
    def log_conversation(
        self,
        conversation_id: str,
        query: str,
        response: str,
        sources: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a conversation exchange.
        
        Args:
            conversation_id: Unique identifier for the conversation
            query: User's question
            response: Chatbot's response
            sources: List of source documents used
            metadata: Additional metadata (e.g., IP, user agent)
        """
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "conversation_id": conversation_id,
                "query": query,
                "response": response,
                "sources_count": len(sources) if sources else 0,
                "sources": self._format_sources(sources) if sources else [],
                "metadata": metadata or {},
            }
            
            # Log to conversation log file
            conversation_logger.info(
                "Conversation logged",
                extra={"conversation": log_entry},
            )
            
            logger.debug(f"Logged conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Failed to log conversation: {str(e)}")
    
    def log_query_start(
        self,
        conversation_id: str,
        query: str,
        client_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log the start of a query processing.
        
        Args:
            conversation_id: Unique identifier for the conversation
            query: User's question
            client_info: Optional client information
        """
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "conversation_id": conversation_id,
                "event": "query_start",
                "query": query,
                "client_info": client_info or {},
            }
            
            conversation_logger.info(
                "Query started",
                extra={"event": log_entry},
            )
            
        except Exception as e:
            logger.error(f"Failed to log query start: {str(e)}")
    
    def log_query_complete(
        self,
        conversation_id: str,
        duration_ms: float,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Log the completion of a query processing.
        
        Args:
            conversation_id: Unique identifier for the conversation
            duration_ms: Processing duration in milliseconds
            success: Whether the query was processed successfully
            error_message: Error message if unsuccessful
        """
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "conversation_id": conversation_id,
                "event": "query_complete",
                "duration_ms": duration_ms,
                "success": success,
                "error_message": error_message,
            }
            
            conversation_logger.info(
                "Query completed",
                extra={"event": log_entry},
            )
            
        except Exception as e:
            logger.error(f"Failed to log query completion: {str(e)}")
    
    def log_error(
        self,
        conversation_id: str,
        error_type: str,
        error_message: str,
        query: Optional[str] = None,
    ) -> None:
        """
        Log an error that occurred during conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            error_type: Type of error
            error_message: Error description
            query: Original query if available
        """
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "conversation_id": conversation_id,
                "event": "error",
                "error_type": error_type,
                "error_message": error_message,
                "query": query,
            }
            
            conversation_logger.error(
                "Conversation error",
                extra={"event": log_entry},
            )
            
        except Exception as e:
            logger.error(f"Failed to log error: {str(e)}")
    
    def _format_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format sources for logging.
        
        Args:
            sources: List of source documents
            
        Returns:
            Formatted sources list
        """
        formatted = []
        for source in sources:
            formatted.append({
                "content_preview": source.get("content", "")[:200],
                "score": source.get("score", 0),
                "metadata": source.get("metadata", {}),
            })
        return formatted


# Singleton instance
_conversation_logger = None


def get_conversation_logger_service() -> ConversationLogger:
    """
    Get the singleton conversation logger instance.
    
    Returns:
        ConversationLogger instance
    """
    global _conversation_logger
    if _conversation_logger is None:
        _conversation_logger = ConversationLogger()
    return _conversation_logger
