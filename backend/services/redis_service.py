"""
Redis service for caching.

Provides Redis connection management and utilities.
"""

import redis
from typing import Optional

from backend.core.logging_config import get_logger

logger = get_logger(__name__)


class RedisService:
    """Service for Redis caching operations."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize Redis service.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Establish Redis connection."""
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=False,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            # Test connection
            self.client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[bytes]:
        """Get value from cache."""
        if not self.is_available():
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.warning(f"Redis GET failed: {e}")
            return None
    
    def set(self, key: str, value: bytes, ttl: int = 3600):
        """Set value in cache with TTL."""
        if not self.is_available():
            return False
        try:
            self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.warning(f"Redis SET failed: {e}")
            return False
    
    def delete(self, key: str):
        """Delete key from cache."""
        if not self.is_available():
            return False
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE failed: {e}")
            return False
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        if not self.is_available():
            return False
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
                logger.info(f"Cleared {len(keys)} keys matching pattern: {pattern}")
            return True
        except Exception as e:
            logger.warning(f"Redis pattern clear failed: {e}")
            return False


# Singleton instance
_redis_service = None


def get_redis_service(redis_url: str = "redis://localhost:6379/0") -> RedisService:
    """
    Get the singleton Redis service instance.
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        RedisService instance
    """
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService(redis_url)
    return _redis_service
