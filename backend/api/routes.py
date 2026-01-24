"""
API routes for the RAG chatbot.

Defines all HTTP endpoints for chat functionality.
"""

import json
import time
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from backend.api.schemas import (
    ChatRequest,
    ChatResponse,
    ErrorResponse,
    HealthResponse,
    Source,
)
from backend.core.exceptions import RAGException
from backend.core.logging_config import get_logger
from backend.rag.chain import get_rag_chain
from backend.rag.vectorstore import get_vectorstore_client
from backend.services.conversation_logger import get_conversation_logger_service

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status of the service
    """
    return HealthResponse(status="healthy")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """
    Process a chat message and return a response.
    
    Args:
        request: Chat request with user message
        http_request: HTTP request for client info
        
    Returns:
        Chat response with answer and sources
    """
    start_time = time.time()
    conversation_id = request.conversation_id or str(uuid4())
    
    # Get conversation logger
    conv_logger = get_conversation_logger_service()
    
    # Log query start
    client_info = {
        "ip": http_request.client.host if http_request.client else None,
        "user_agent": http_request.headers.get("user-agent"),
    }
    conv_logger.log_query_start(conversation_id, request.message, client_info)
    
    logger.info(f"Received chat request (conversation_id={conversation_id})")
    
    try:
        # Process query through RAG chain
        rag_chain = get_rag_chain()
        result = rag_chain.process_query(
            query=request.message,
            conversation_id=conversation_id,
        )
        
        response_text = result["response"]
        conv_id = result["conversation_id"]
        sources = result["sources"]
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log conversation
        conv_logger.log_conversation(
            conversation_id=conv_id,
            query=request.message,
            response=response_text,
            sources=[s.model_dump() for s in sources],
            metadata=client_info,
        )
        conv_logger.log_query_complete(conv_id, duration_ms, success=True)
        
        logger.info(f"Chat request completed in {duration_ms:.2f}ms")
        
        return ChatResponse(
            response=response_text,
            conversation_id=conv_id,
            sources=sources,
        )
        
    except RAGException as e:
        duration_ms = (time.time() - start_time) * 1000
        conv_logger.log_error(
            conversation_id=conversation_id,
            error_type=type(e).__name__,
            error_message=e.message,
            query=request.message,
        )
        conv_logger.log_query_complete(
            conversation_id, duration_ms, success=False, error_message=e.message
        )
        
        logger.error(f"Chat request failed: {e.message}")
        raise HTTPException(status_code=500, detail=e.message)
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        conv_logger.log_error(
            conversation_id=conversation_id,
            error_type="UnexpectedError",
            error_message=str(e),
            query=request.message,
        )
        conv_logger.log_query_complete(
            conversation_id, duration_ms, success=False, error_message=str(e)
        )
        
        logger.error(f"Unexpected error in chat request: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, http_request: Request):
    """
    Process a chat message and stream the response.
    
    Args:
        request: Chat request with user message
        http_request: HTTP request for client info
        
    Returns:
        Streaming response with answer chunks
    """
    conversation_id = request.conversation_id or str(uuid4())
    
    # Get conversation logger
    conv_logger = get_conversation_logger_service()
    
    # Log query start
    client_info = {
        "ip": http_request.client.host if http_request.client else None,
        "user_agent": http_request.headers.get("user-agent"),
    }
    conv_logger.log_query_start(conversation_id, request.message, client_info)
    
    logger.info(f"Received streaming chat request (conversation_id={conversation_id})")
    
    async def generate():
        start_time = time.time()
        full_response = ""
        sources = []
        
        try:
            rag_chain = get_rag_chain()
            
            for chunk, is_final, conv_id, chunk_sources in rag_chain.process_query_stream(
                query=request.message,
                conversation_id=conversation_id,
            ):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'content': chunk, 'is_final': False})}\n\n"
                
                if is_final:
                    sources = chunk_sources
                    yield f"data: {json.dumps({'content': '', 'is_final': True, 'conversation_id': conv_id, 'sources': [s.model_dump() for s in sources]})}\n\n"
            
            # Log conversation
            duration_ms = (time.time() - start_time) * 1000
            conv_logger.log_conversation(
                conversation_id=conversation_id,
                query=request.message,
                response=full_response,
                sources=[s.model_dump() for s in sources],
                metadata=client_info,
            )
            conv_logger.log_query_complete(conversation_id, duration_ms, success=True)
            
            logger.info(f"Streaming chat completed in {duration_ms:.2f}ms")
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            conv_logger.log_error(
                conversation_id=conversation_id,
                error_type=type(e).__name__,
                error_message=str(e),
                query=request.message,
            )
            conv_logger.log_query_complete(
                conversation_id, duration_ms, success=False, error_message=str(e)
            )
            
            logger.error(f"Error in streaming chat: {str(e)}")
            yield f"data: {json.dumps({'error': str(e), 'is_final': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-ID": conversation_id,
        },
    )


@router.get("/stats")
async def get_stats():
    """
    Get vector store statistics.
    
    Returns:
        Collection statistics
    """
    try:
        vectorstore = get_vectorstore_client()
        info = vectorstore.get_collection_info()
        return info
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")
