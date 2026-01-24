"""
Proxy configuration module.

Handles proxy setup for corporate networks.
Toggle USE_PROXY in .env to enable/disable.
"""

import os
from urllib.parse import quote

from backend.core.logging_config import get_logger

logger = get_logger(__name__)


def configure_proxy() -> bool:
    """
    Configure proxy settings from environment variables.
    
    Set USE_PROXY=true in .env to enable.
    Set USE_PROXY=false or remove it to disable.
    
    Returns:
        True if proxy was configured, False otherwise
    """
    use_proxy = os.getenv("USE_PROXY", "false").lower() == "true"
    
    if not use_proxy:
        # Clear any existing proxy settings
        for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
            if var in os.environ:
                del os.environ[var]
        logger.info("Proxy disabled")
        return False
    
    # Get proxy settings
    proxy_host = os.getenv("PROXY_HOST")
    proxy_port = os.getenv("PROXY_PORT", "80")
    proxy_username = os.getenv("PROXY_USERNAME")
    proxy_password = os.getenv("PROXY_PASSWORD")
    
    if not proxy_host:
        logger.warning("USE_PROXY=true but PROXY_HOST not set")
        return False
    
    # Build proxy URL
    if proxy_username and proxy_password:
        # URL-encode username and password (handles special chars like @ in email)
        encoded_username = quote(proxy_username, safe="")
        encoded_password = quote(proxy_password, safe="")
        proxy_url = f"http://{encoded_username}:{encoded_password}@{proxy_host}:{proxy_port}"
        logger.info(f"Proxy configured: {proxy_host}:{proxy_port} (authenticated)")
    else:
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        logger.info(f"Proxy configured: {proxy_host}:{proxy_port} (no auth)")
    
    # Set environment variables
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    os.environ["http_proxy"] = proxy_url
    os.environ["https_proxy"] = proxy_url
    
    return True


def get_proxy_dict() -> dict | None:
    """
    Get proxy settings as a dictionary for requests/httpx.
    
    Returns:
        Proxy dict or None if proxy disabled
    """
    use_proxy = os.getenv("USE_PROXY", "false").lower() == "true"
    
    if not use_proxy:
        return None
    
    proxy_url = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    
    if proxy_url:
        return {
            "http://": proxy_url,
            "https://": proxy_url,
        }
    
    return None
