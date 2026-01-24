"""
Groq LLM client.

Handles LLM inference using Groq API with streaming support.
"""

from typing import AsyncGenerator, List, Optional

from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.config import get_settings
from backend.core.exceptions import LLMError
from backend.core.logging_config import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Client for LLM inference using Groq API."""
    
    def __init__(self, model_name: Optional[str] = None, temperature: Optional[float] = None):
        """
        Initialize the Groq client.
        
        Args:
            model_name: Optional custom model name
            temperature: Optional custom temperature
        """
        settings = get_settings()
        
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = model_name or settings.groq_model
        self.max_tokens = settings.groq_max_tokens
        self.temperature = temperature if temperature is not None else settings.groq_temperature
        
        logger.info(f"Initialized LLMClient with model: {self.model}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda retry_state: logger.warning(
            f"LLM call failed, retrying... (attempt {retry_state.attempt_number}/3)"
        ),
    )
    def generate(
        self,
        messages: List[dict],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate a response from the LLM with automatic retry on failure.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Override default max tokens (optional)
            temperature: Override default temperature (optional)
            
        Returns:
            Generated response text
            
        Raises:
            LLMError: If generation fails after retries
        """
        try:
            logger.debug(f"Generating response with {len(messages)} messages")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )
            
            content = response.choices[0].message.content
            
            logger.debug(f"Generated response with {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise LLMError(
                message="Failed to generate LLM response",
                details={"error": str(e), "model": self.model},
            )
    
    def generate_stream(
        self,
        messages: List[dict],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        """
        Generate a streaming response from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Override default max tokens (optional)
            temperature: Override default temperature (optional)
            
        Yields:
            Response text chunks
            
        Raises:
            LLMError: If generation fails
        """
        try:
            logger.debug(f"Generating streaming response with {len(messages)} messages")
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.debug("Completed streaming response")
            
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {str(e)}")
            raise LLMError(
                message="Failed to generate streaming LLM response",
                details={"error": str(e), "model": self.model},
            )


# Singleton instance
_llm_client = None


def get_llm_client(model_name: Optional[str] = None, temperature: Optional[float] = None) -> LLMClient:
    """
    Get the singleton LLM client instance.
    
    Args:
        model_name: Optional custom model name
        temperature: Optional custom temperature
        
    Returns:
        LLMClient instance
    """
    global _llm_client
    # Create new instance if parameters are provided (non-singleton mode for custom settings)
    if model_name or temperature is not None:
        return LLMClient(model_name=model_name, temperature=temperature)
    
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
