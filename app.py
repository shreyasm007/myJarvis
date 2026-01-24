"""
Streamlit Admin Dashboard for RAG Chatbot.

Modular frontend with organized components.
"""

import sys
from pathlib import Path

import streamlit as st

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / ".env")

# Configure proxy if needed
from backend.core.proxy_config import configure_proxy
configure_proxy()

# Import frontend components
from frontend.config import PAGE_CONFIG, init_session_state, apply_custom_css
from frontend.sidebar import render_sidebar
from frontend.tabs.chat import render_chat_tab
from frontend.tabs.logs import render_logs_tab
from frontend.tabs.analytics import render_analytics_tab
from frontend.tabs.documents import render_documents_tab


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Apply custom CSS
    apply_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar and get settings
    settings = render_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📄 Logs", "📊 Analytics", "📁 Documents"])
    
    with tab1:
        render_chat_tab(settings)
    
    with tab2:
        render_logs_tab()
    
    with tab3:
        render_analytics_tab()
    
    with tab4:
        render_documents_tab()


if __name__ == "__main__":
    main()
