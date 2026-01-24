"""
Configuration and initialization for Streamlit frontend.
"""

import streamlit as st
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Page configuration
PAGE_CONFIG = {
    "page_title": "RAG Chatbot Admin",
    "page_icon": "💬",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Custom CSS styles
CUSTOM_CSS = """
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
    .retrieved-context {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #4F46E5;
        margin: 10px 0;
    }
    .log-entry {
        font-family: monospace;
        font-size: 12px;
        padding: 5px;
        margin: 2px 0;
    }
    .error { color: #ff4444; }
    .warning { color: #ffaa00; }
    .info { color: #4444ff; }
    .success { color: #00cc66; }
</style>
"""

# LLM Model options
LLM_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

def init_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "retrieved_contexts" not in st.session_state:
        st.session_state.retrieved_contexts = []

def apply_custom_css():
    """Apply custom CSS styles."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
