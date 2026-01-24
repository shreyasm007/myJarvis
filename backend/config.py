"""
Application configuration using Pydantic Settings.

Loads environment variables and provides type-safe access
to all configuration values.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Groq API (LLM)
    groq_api_key: str = Field(
        ...,
        description="Groq API key for LLM inference",
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model to use",
    )
    groq_max_tokens: int = Field(
        default=1024,
        description="Maximum tokens in LLM response",
    )
    groq_temperature: float = Field(
        default=0.7,
        description="LLM temperature for response generation",
    )
    
    # Voyage AI (Embeddings)
    voyage_api_key: str = Field(
        ...,
        description="Voyage AI API key for embeddings",
    )
    voyage_model: str = Field(
        default="voyage-3-lite",
        description="Voyage embedding model to use",
    )
    
    # Qdrant Cloud (Vector Store)
    qdrant_url: str = Field(
        ...,
        description="Qdrant Cloud cluster URL",
    )
    qdrant_api_key: str = Field(
        ...,
        description="Qdrant Cloud API key",
    )
    qdrant_collection_name: str = Field(
        default="portfolio",
        description="Qdrant collection name",
    )
    
    # RAG Settings
    rag_top_k: int = Field(
        default=5,
        description="Number of documents to retrieve",
    )
    rag_score_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for retrieval",
    )
    
    # Application Settings
    app_env: str = Field(
        default="development",
        description="Application environment",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    
    Returns:
        Settings instance with loaded configuration
    """
    return Settings()
