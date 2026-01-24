"""
Sidebar component for settings and controls.
"""

import streamlit as st

from frontend.config import LLM_MODELS
from frontend.utils import get_db_stats


def render_sidebar():
    """
    Render the sidebar with settings and controls.
    
    Returns:
        Dictionary with selected settings
    """
    with st.sidebar:
        st.title("💬 RAG Admin")
        st.markdown("---")
        
        # Settings
        st.header("⚙️ Settings")
        
        # LLM Model Selection
        selected_model = st.selectbox(
            "LLM Model",
            LLM_MODELS,
            index=0,
            help="Select the Groq model to use for responses"
        )
        
        # Temperature
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher = more creative, Lower = more focused"
        )
        
        # Top K for retrieval
        top_k = st.slider(
            "Retrieved Documents (Top K)",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of relevant documents to retrieve"
        )
        
        # Score threshold
        score_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05,
            help="Minimum similarity score for retrieved documents"
        )
        
        st.markdown("---")
        
        # Database Stats
        st.header("📊 Database Stats")
        stats = get_db_stats()
        
        if "error" in stats:
            st.error(f"Error: {stats['error']}")
        else:
            st.metric("Collection", stats.get("name", "N/A"))
            st.metric("Total Documents", stats.get("points_count", 0))
            st.metric("Status", stats.get("status", "Unknown"))
        
        st.markdown("---")
        
        # Quick Actions
        st.header("🔧 Quick Actions")
        
        if st.button("🔄 Refresh Stats", use_container_width=True):
            st.rerun()
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.retrieved_contexts = []
            st.rerun()
    
    return {
        "model": selected_model,
        "temperature": temperature,
        "top_k": top_k,
        "score_threshold": score_threshold,
    }
