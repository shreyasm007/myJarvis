"""
API client for communicating with the FastAPI backend.

All frontend-to-backend communication goes through HTTP calls.
"""

import os
import httpx
from typing import Dict, Any, Optional
from urllib.parse import quote


class APIClient:
    """Client for making HTTP requests to the FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the FastAPI backend
        """
        self.base_url = base_url
        
        # Configure proxy based on USE_PROXY environment variable (same as backend)
        use_proxy = os.getenv("USE_PROXY", "false").lower() == "true"
        
        if use_proxy:
            # Use proxy configuration from .env
            proxy_host = os.getenv("PROXY_HOST")
            proxy_port = os.getenv("PROXY_PORT")
            proxy_username = os.getenv("PROXY_USERNAME")
            proxy_password = os.getenv("PROXY_PASSWORD")
            
            if proxy_host and proxy_port:
                if proxy_username and proxy_password:
                    # URL-encode credentials to handle special characters
                    encoded_user = quote(proxy_username, safe='')
                    encoded_pass = quote(proxy_password, safe='')
                    proxy_url = f"http://{encoded_user}:{encoded_pass}@{proxy_host}:{proxy_port}"
                else:
                    proxy_url = f"http://{proxy_host}:{proxy_port}"
                
                self.client = httpx.Client(
                    timeout=30.0,
                    proxies={"http://": proxy_url, "https://": proxy_url}
                )
            else:
                # Proxy enabled but not configured, use environment
                self.client = httpx.Client(timeout=30.0, trust_env=True)
        else:
            # No proxy, use direct connection (USE_PROXY=false)
            self.client = httpx.Client(timeout=30.0, trust_env=False)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the backend is healthy.
        
        Returns:
            Health status response
        """
        try:
            response = self.client.get(f"{self.base_url}/api/v1/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        chat_history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Send a chat message to the backend.
        
        Args:
            message: User message
            conversation_id: Optional conversation ID
            chat_history: Optional conversation history [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            Chat response with answer and sources
        """
        try:
            payload = {
                "message": message,
                "conversation_id": conversation_id or "streamlit-session",
                "chat_history": chat_history or []
            }
            response = self.client.post(
                f"{self.base_url}/api/v1/chat",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "conversation_id": conversation_id or "error",
                "sources": []
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Database statistics
        """
        try:
            response = self.client.get(f"{self.base_url}/api/v1/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


# Singleton instance
_api_client = None


def get_api_client(base_url: str = "http://localhost:8000") -> APIClient:
    """
    Get the singleton API client instance.
    
    Args:
        base_url: Base URL of the FastAPI backend
        
    Returns:
        APIClient instance
    """
    global _api_client
    if _api_client is None:
        _api_client = APIClient(base_url)
    return _api_client
