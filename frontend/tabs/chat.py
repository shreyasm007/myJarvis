"""
Chat interface tab component.
"""

import streamlit as st

from frontend.api_client import get_api_client


def render_chat_tab(settings: dict):
    """
    Render the interactive chat interface.
    
    Args:
        settings: Dictionary with user-selected settings (currently not used by API)
    """
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
        
        # Get response from backend API
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Call backend API
                    api_client = get_api_client()
                    response_data = api_client.chat(message=prompt)
                    
                    response = response_data.get("response", "No response received")
                    sources = response_data.get("sources", [])
                    
                    # Display response
                    st.markdown(response)
                    
                    # Store message and context
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.retrieved_contexts.append(sources)
                    
                    # Show retrieved context
                    if sources:
                        with st.expander(f"📚 Retrieved Context ({len(sources)} documents)", expanded=True):
                            for i, source in enumerate(sources):
                                st.markdown(f"""
                                <div class="retrieved-context">
                                    <strong>Document {i+1}</strong> (Score: {source.get('score', 0):.3f})<br/>
                                    <strong>Source:</strong> {source.get('metadata', {}).get('source', 'Unknown')}<br/>
                                    <strong>Content:</strong> {source.get('content', '')[:500]}...
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ No relevant context found in database. Check if documents are ingested.")
                
                except Exception as e:
                    error_msg = f"Error communicating with backend: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.session_state.retrieved_contexts.append([])
