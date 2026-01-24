"""
Pydantic schemas for API request and response models.

Defines the data structures for chat endpoint communication.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single message in conversation history."""
    
    role: str = Field(
        ...,
        description="Message role: 'user' or 'assistant'",
    )
    content: str = Field(
        ...,
        description="Message content",
    )


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message/question",
        examples=["What projects have you worked on?"],
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID for tracking",
    )
    chat_history: Optional[List['ChatMessage']] = Field(
        default_factory=list,
        description="Previous conversation messages for context",
    )


class Source(BaseModel):
    """Source document reference in response."""
    
    content: str = Field(
        ...,
        description="Relevant content snippet from source",
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance score",
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional metadata about the source",
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    
    response: str = Field(
        ...,
        description="Chatbot's response message",
    )
    conversation_id: str = Field(
        ...,
        description="Conversation ID for tracking",
    )
    sources: List[Source] = Field(
        default_factory=list,
        description="Source documents used in response",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp",
    )


class StreamChunk(BaseModel):
    """Model for streaming response chunks."""
    
    content: str = Field(
        ...,
        description="Chunk of response text",
    )
    is_final: bool = Field(
        default=False,
        description="Whether this is the final chunk",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation ID (included in final chunk)",
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(
        default="healthy",
        description="Service health status",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp",
    )
    version: str = Field(
        default="1.0.0",
        description="API version",
    )


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    
    error: str = Field(
        ...,
        description="Error message",
    )
    detail: Optional[str] = Field(
        default=None,
        description="Detailed error information",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp",
    )
