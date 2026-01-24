"""
Streamlit Admin Dashboard for RAG Chatbot.

Features:
- Interactive chat interface with retrieved context display
- Real-time log viewer
- Settings management (LLM model, parameters)
- Database statistics and monitoring
- Document management
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / ".env")

# Configure proxy if needed
from backend.core.proxy_config import configure_proxy
configure_proxy()

from backend.config import get_settings
from backend.rag.chain import RAGChain
from backend.rag.embeddings import get_embeddings_client
from backend.rag.retriever import get_retriever
from backend.rag.vectorstore import get_vectorstore_client

# Page config
st.set_page_config(
    page_title="RAG Chatbot Admin",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
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
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "retrieved_contexts" not in st.session_state:
    st.session_state.retrieved_contexts = []


def load_logs(log_file: str, tail_lines: int = 100) -> list:
    """Load the last N lines from a log file."""
    log_path = project_root / "logs" / log_file
    if not log_path.exists():
        return []
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines[-tail_lines:]
    except Exception as e:
        return [f"Error reading log: {str(e)}"]


def parse_log_entry(line: str) -> dict:
    """Parse a JSON log entry."""
    try:
        return json.loads(line)
    except:
        return {"message": line.strip(), "levelname": "INFO"}


def get_db_stats():
    """Get database statistics."""
    try:
        vectorstore = get_vectorstore_client()
        info = vectorstore.get_collection_info()
        return info
    except Exception as e:
        return {"error": str(e)}


# Sidebar
with st.sidebar:
    st.title("💬 RAG Admin")
    st.markdown("---")
    
    # Settings
    st.header("⚙️ Settings")
    
    # LLM Model Selection
    llm_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]
    
    selected_model = st.selectbox(
        "LLM Model",
        llm_models,
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
        value=0.7,
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


# Main content
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📄 Logs", "📊 Analytics", "📁 Documents"])

# Tab 1: Chat Interface
with tab1:
    st.header("Interactive Chat")
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show retrieved context for assistant messages
            if message["role"] == "assistant" and idx < len(st.session_state.retrieved_contexts):
                contexts = st.session_state.retrieved_contexts[idx]
                if contexts:
                    with st.expander(f"📚 Retrieved Context ({len(contexts)} documents)", expanded=False):
                        for i, ctx in enumerate(contexts):
                            st.markdown(f"""
                            <div class="retrieved-context">
                                <strong>Document {i+1}</strong> (Score: {ctx.get('score', 0):.3f})<br/>
                                <strong>Source:</strong> {ctx.get('metadata', {}).get('source', 'Unknown')}<br/>
                                <strong>Content:</strong> {ctx.get('content', '')[:500]}...
                            </div>
                            """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Initialize RAG components with settings
                    embeddings_client = get_embeddings_client()
                    vectorstore_client = get_vectorstore_client()
                    retriever = get_retriever(
                        embeddings_client=embeddings_client,
                        vectorstore_client=vectorstore_client,
                        top_k=top_k,
                        score_threshold=score_threshold,
                    )
                    
                    # Set model in environment
                    os.environ["GROQ_MODEL_NAME"] = selected_model
                    
                    # Create RAG chain
                    rag_chain = RAGChain(
                        retriever=retriever,
                        embeddings_client=embeddings_client,
                        model_name=selected_model,
                        temperature=temperature,
                    )
                    
                    # Get response and context
                    response_data = rag_chain.process_query(prompt)
                    response = response_data["response"]
                    contexts = response_data.get("contexts", [])
                    
                    # Display response
                    st.markdown(response)
                    
                    # Store message and context
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.retrieved_contexts.append(contexts)
                    
                    # Show retrieved context
                    if contexts:
                        with st.expander(f"📚 Retrieved Context ({len(contexts)} documents)", expanded=True):
                            for i, ctx in enumerate(contexts):
                                st.markdown(f"""
                                <div class="retrieved-context">
                                    <strong>Document {i+1}</strong> (Score: {ctx.get('score', 0):.3f})<br/>
                                    <strong>Source:</strong> {ctx.get('metadata', {}).get('source', 'Unknown')}<br/>
                                    <strong>Content:</strong> {ctx.get('content', '')[:500]}...
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ No relevant context found in database. Check if documents are ingested.")
                
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.session_state.retrieved_contexts.append([])

# Tab 2: Logs
with tab2:
    st.header("📄 Application Logs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Application Logs")
        tail_lines_app = st.slider("Lines to show", 10, 500, 100, key="app_log_lines")
        
        if st.button("Refresh App Logs", use_container_width=True):
            st.rerun()
        
        app_logs = load_logs("app.log", tail_lines_app)
        
        # Parse and display with color coding
        for line in app_logs:
            entry = parse_log_entry(line)
            level = entry.get("levelname", "INFO")
            message = entry.get("message", line)
            
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
        
        conv_logs = load_logs("conversations.log", tail_lines_conv)
        
        for line in conv_logs:
            st.markdown(f'<div class="log-entry">{line.strip()}</div>', unsafe_allow_html=True)

# Tab 3: Analytics
with tab3:
    st.header("📊 Analytics Dashboard")
    
    # Parse conversation logs for analytics
    conv_logs = load_logs("conversations.log", 1000)
    conversations = []
    
    for line in conv_logs:
        entry = parse_log_entry(line)
        if "query" in entry:
            conversations.append(entry)
    
    if conversations:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Conversations", len(conversations))
        
        with col2:
            with_context = sum(1 for c in conversations if c.get("sources"))
            st.metric("With Retrieved Context", with_context)
        
        with col3:
            without_context = len(conversations) - with_context
            st.metric("Fallback Responses", without_context)
        
        # Query length distribution
        st.subheader("Query Length Distribution")
        query_lengths = [len(c.get("query", "")) for c in conversations]
        
        fig = px.histogram(
            x=query_lengths,
            nbins=20,
            title="Distribution of Query Lengths",
            labels={"x": "Query Length (characters)", "y": "Count"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Context retrieval success rate
        st.subheader("Context Retrieval Success Rate")
        
        fig = go.Figure(data=[go.Pie(
            labels=["With Context", "No Context"],
            values=[with_context, without_context],
            hole=.3
        )])
        fig.update_layout(title="Retrieval Success Rate")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No conversation data available yet. Start chatting to see analytics!")

# Tab 4: Documents
with tab4:
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
    docs_dir = project_root / "backend" / "data" / "documents"
    
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
