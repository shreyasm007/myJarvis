"""
Analytics dashboard tab component.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from frontend.utils import load_logs, parse_log_entry
from frontend.config import PROJECT_ROOT


def render_analytics_tab():
    """Render the analytics dashboard."""
    st.header("📊 Analytics Dashboard")
    
    # Parse conversation logs for analytics
    conv_logs = load_logs("conversations.log", 1000, PROJECT_ROOT)
    conversations = []
    
    for line in conv_logs:
        entry = parse_log_entry(line)
        # Check if this is a conversation log entry (not query_start or query_complete)
        if entry.get("message") == "Conversation logged" and "conversation" in entry:
            conv_data = entry["conversation"]
            conversations.append(conv_data)
    
    if conversations:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Conversations", len(conversations))
        
        with col2:
            with_context = sum(1 for c in conversations if c.get("sources_count", 0) > 0)
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
        
        # Recent conversations table
        st.subheader("Recent Conversations")
        recent = conversations[-10:]  # Last 10
        for i, conv in enumerate(reversed(recent), 1):
            with st.expander(f"💬 {i}. {conv.get('query', 'Unknown')[:50]}..."):
                st.write(f"**Query:** {conv.get('query', 'N/A')}")
                st.write(f"**Response:** {conv.get('response', 'N/A')[:300]}...")
                st.write(f"**Sources:** {conv.get('sources_count', 0)} documents")
                st.write(f"**Timestamp:** {conv.get('timestamp', 'N/A')}")
        
    else:
        st.info("No conversation data available yet. Start chatting to see analytics!")
