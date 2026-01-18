
import streamlit as st
from utils.ai_helper import get_medicine_search
from utils.styling import render_sidebar_header

def render_ai_sidebar():
    """
    Renders the AI Assistant in the sidebar.
    Contains chat history and input logic.
    """
    
    # Ensure sidebar header is always there first
    render_sidebar_header(st)

    # Initialize session state for chat if needed
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'medicine_search' not in st.session_state:
        st.session_state.medicine_search = get_medicine_search()

    st.sidebar.markdown("### 🤖 AI Assistant")
    st.sidebar.markdown("*Ask me about any medicine!*")

    # Scrollable chat container
    with st.sidebar.container(height=350):
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**AI:** {msg['content']}")
                st.markdown("---")

    # Chat input
    user_query = st.sidebar.chat_input("Ask about medicines...", key="global_sidebar_chat")
    if user_query:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Get response (handles tool calls internally)
        response = st.session_state.medicine_search.answer_query(user_query)
        
        # Add AI response
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Check for success message to show toast
        if "✅" in response:
            st.toast(response, icon="✅")
        
        st.rerun()
