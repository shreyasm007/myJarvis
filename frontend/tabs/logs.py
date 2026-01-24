"""
Logs viewer tab component.
"""

import streamlit as st

from frontend.utils import load_logs, parse_log_entry
from frontend.config import PROJECT_ROOT


def render_logs_tab():
    """Render the logs viewer interface."""
    st.header("📄 Application Logs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Application Logs")
        tail_lines_app = st.slider("Lines to show", 10, 500, 100, key="app_log_lines")
        
        if st.button("Refresh App Logs", use_container_width=True):
            st.rerun()
        
        app_logs = load_logs("app.log", tail_lines_app, PROJECT_ROOT)
        
        # Parse and display with color coding
        for line in app_logs:
            entry = parse_log_entry(line)
            level = entry.get("levelname", "INFO")
            
            css_class = {
                "ERROR": "error",
                "WARNING": "warning",
                "INFO": "info",
            }.get(level, "info")
            
            st.markdown(f'<div class="log-entry {css_class}">{line.strip()}</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Conversation Logs")
        tail_lines_conv = st.slider("Lines to show", 10, 500, 100, key="conv_log_lines")
        
        if st.button("Refresh Conversation Logs", use_container_width=True):
            st.rerun()
        
        conv_logs = load_logs("conversations.log", tail_lines_conv, PROJECT_ROOT)
        
        for line in conv_logs:
            st.markdown(f'<div class="log-entry">{line.strip()}</div>', unsafe_allow_html=True)
