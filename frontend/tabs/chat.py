"""
Chat interface tab component.
"""

import streamlit as st
import json

from frontend.api_client import get_api_client


def render_chat_tab(settings: dict):
    """
    Render the interactive chat interface.
    
    Args:
        settings: Dictionary with user-selected settings (currently not used by API)
    """
    st.header("Interactive Chat")
    
    # Streaming mode toggle
    use_streaming = st.toggle("⚡ Enable Streaming (Real-time response)", value=True)
    
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
            message_placeholder = st.empty()
            
            if use_streaming:
                # Streaming mode - progressive display
                full_response = ""
                sources = []
                
                try:
                    # Prepare chat history
                    chat_history = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages[:-1]
                    ]
                    
                    # Call streaming endpoint
                    api_client = get_api_client()
                    
                    with api_client.client.stream(
                        "POST",
                        f"{api_client.base_url}/api/v1/chat/stream",
                        json={
                            "message": prompt,
                            "conversation_id": "streamlit-session",
                            "chat_history": chat_history
                        }
                    ) as response:
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                data = json.loads(line[6:])
                                if data.get("content"):
                                    full_response += data["content"]
                                    message_placeholder.markdown(full_response + "▌")
                                if data.get("is_final"):
                                    sources = data.get("sources", [])
                                    break
                    
                    # Final display without cursor
                    message_placeholder.markdown(full_response)
                    
                    # Store message
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.session_state.retrieved_contexts.append(sources)
                    
                    # Show sources
                    if sources:
                        with st.expander(f"📚 Retrieved Context ({len(sources)} documents)", expanded=False):
                            for i, source in enumerate(sources):
                                st.markdown(f"""
                                <div class="retrieved-context">
                                    <strong>Document {i+1}</strong> (Score: {source.get('score', 0):.3f})<br/>
                                    <strong>Source:</strong> {source.get('metadata', {}).get('source', 'Unknown')}<br/>
                                    <strong>Content:</strong> {source.get('content', '')[:500]}...
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ No relevant context found in database.")
                
                except Exception as e:
                    error_msg = f"Error with streaming: {str(e)}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.session_state.retrieved_contexts.append([])
            else:
                # Standard mode - wait for full response
                with st.spinner("Thinking..."):
                    try:
                        # Prepare chat history (exclude current message)
                        chat_history = [
                            {"role": msg["role"], "content": msg["content"]}
                            for msg in st.session_state.messages[:-1]  # Exclude the just-added user message
                        ]
                        
                        # Call backend API with conversation history
                        api_client = get_api_client()
                        response_data = api_client.chat(
                            message=prompt,
                            chat_history=chat_history
                        )
                        
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
