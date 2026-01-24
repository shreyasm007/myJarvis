"""
Documents management tab component.
"""

from datetime import datetime
from pathlib import Path

import streamlit as st

from frontend.utils import get_db_stats
from frontend.config import PROJECT_ROOT


def render_documents_tab():
    """Render the document management interface."""
    st.header("📁 Document Management")
    
    st.subheader("Collection Information")
    stats = get_db_stats()
    
    if "error" not in stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Collection Name", stats.get("name", "N/A"))
        with col2:
            st.metric("Total Vectors", stats.get("points_count", 0))
        with col3:
            st.metric("Status", stats.get("status", "Unknown"))
    
    st.markdown("---")
    
    st.subheader("Document Source Directory")
    docs_dir = PROJECT_ROOT / "backend" / "data" / "documents"
    
    if docs_dir.exists():
        files = list(docs_dir.glob("*"))
        
        if files:
            st.success(f"Found {len(files)} file(s) in documents directory")
            
            for file in files:
                if file.is_file():
                    with st.expander(f"📄 {file.name}"):
                        st.text(f"Size: {file.stat().st_size} bytes")
                        st.text(f"Modified: {datetime.fromtimestamp(file.stat().st_mtime)}")
                        
                        if file.suffix.lower() in ['.txt', '.md', '.markdown']:
                            try:
                                content = file.read_text(encoding='utf-8')
                                st.text_area("Preview", content[:1000] + "..." if len(content) > 1000 else content, height=200)
                            except Exception as e:
                                st.error(f"Error reading file: {e}")
        else:
            st.warning("No documents found in directory")
    else:
        st.error(f"Documents directory does not exist: {docs_dir}")
    
    st.markdown("---")
    
    st.subheader("Re-ingest Documents")
    st.info("💡 To re-ingest documents, run: `python -m scripts.ingest`")
    
    if st.button("📋 Copy Command to Clipboard", use_container_width=True):
        st.code("python -m scripts.ingest", language="bash")
