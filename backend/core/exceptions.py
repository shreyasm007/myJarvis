"""
Custom exceptions for the RAG chatbot application.

Provides specific exception classes for different error scenarios
to enable proper error handling and logging.
"""


class RAGException(Exception):
    """Base exception for all RAG-related errors."""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EmbeddingError(RAGException):
    """Exception raised when embedding generation fails."""
    
    def __init__(self, message: str = "Failed to generate embeddings", details: dict = None):
        super().__init__(message, details)


class VectorStoreError(RAGException):
    """Exception raised when vector store operations fail."""
    
    def __init__(self, message: str = "Vector store operation failed", details: dict = None):
        super().__init__(message, details)


class RetrievalError(RAGException):
    """Exception raised when document retrieval fails."""
    
    def __init__(self, message: str = "Document retrieval failed", details: dict = None):
        super().__init__(message, details)


class LLMError(RAGException):
    """Exception raised when LLM inference fails."""
    
    def __init__(self, message: str = "LLM inference failed", details: dict = None):
        super().__init__(message, details)


class ConfigurationError(RAGException):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str = "Configuration error", details: dict = None):
        super().__init__(message, details)


class DocumentIngestionError(RAGException):
    """Exception raised when document ingestion fails."""
    
    def __init__(self, message: str = "Document ingestion failed", details: dict = None):
        super().__init__(message, details)


class OutOfScopeError(RAGException):
    """Exception raised when query is outside the chatbot's scope."""
    
    def __init__(self, message: str = "Query is outside the chatbot's scope", details: dict = None):
        super().__init__(message, details)
