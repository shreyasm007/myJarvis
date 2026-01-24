"""
Chat interface tab component.
"""

import os
import streamlit as st

from backend.rag.chain import RAGChain
from backend.rag.embeddings import get_embeddings_client
from backend.rag.retriever import get_retriever
from backend.rag.vectorstore import get_vectorstore_client


def render_chat_tab(settings: dict):
    """
    Render the interactive chat interface.
    
    Args:
        settings: Dictionary with user-selected settings
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
                        top_k=settings["top_k"],
                        score_threshold=settings["score_threshold"],
                    )
                    
                    # Set model in environment
                    os.environ["GROQ_MODEL_NAME"] = settings["model"]
                    
                    # Create RAG chain
                    rag_chain = RAGChain(
                        retriever=retriever,
                        embeddings_client=embeddings_client,
                        model_name=settings["model"],
                        temperature=settings["temperature"],
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
