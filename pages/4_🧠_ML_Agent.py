"""
Remidex - ML Agent (Knowledge Hub) Page
AI-powered medicine search and information
"""

import streamlit as st
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import Database
from utils.ai_helper import get_medicine_search

# Page configuration
st.set_page_config(
    page_title="Knowledge Hub | Remidex",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --lime-green: #32CD32;
        --black: #000000;
        --white: #FFFFFF;
        --dark-gray: #1a1a1a;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--dark-gray);
        border-right: 2px solid var(--lime-green);
    }
    
    h1, h2, h3, h4 { color: var(--lime-green) !important; }
    
    .search-container {
        background: linear-gradient(145deg, var(--dark-gray), #0d0d0d);
        border: 2px solid var(--lime-green);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .result-card {
        background: var(--dark-gray);
        border: 1px solid var(--lime-green);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .medicine-title {
        color: var(--lime-green);
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .info-section {
        background: rgba(50, 205, 50, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid var(--lime-green);
    }
    
    .info-title {
        color: var(--lime-green);
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .info-content {
        color: rgba(255,255,255,0.9);
        line-height: 1.6;
    }
    
    .side-effects-list {
        color: #ffcc00;
    }
    
    .interaction-warning {
        background: rgba(255, 107, 107, 0.2);
        border-left-color: #ff6b6b;
    }
    
    .interaction-title {
        color: #ff6b6b;
    }
    
    .match-score {
        background: var(--lime-green);
        color: var(--black);
        padding: 0.2rem 0.6rem;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .stButton > button {
        background: linear-gradient(145deg, var(--lime-green), #28a428);
        color: var(--black) !important;
        font-weight: 600;
        border: none;
        border-radius: 10px;
    }
    
    .chat-message-user {
        background: var(--lime-green);
        color: var(--black);
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
    }
    
    .chat-message-ai {
        background: var(--dark-gray);
        border: 1px solid var(--lime-green);
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        color: var(--white);
    }
    
    .quick-query-btn {
        background: transparent !important;
        border: 1px solid var(--lime-green) !important;
        color: var(--lime-green) !important;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()
if 'medicine_search' not in st.session_state:
    st.session_state.medicine_search = get_medicine_search()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'kb_chat_history' not in st.session_state:
    st.session_state.kb_chat_history = []

# Sidebar
st.sidebar.markdown("# 💊 Remidex")
st.sidebar.markdown("*Your Smart Medication Manager*")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🤖 AI Assistant")
for msg in st.session_state.chat_history[-3:]:
    if msg["role"] == "user":
        st.sidebar.markdown(f"**You:** {msg['content'][:40]}...")
    else:
        st.sidebar.markdown(f"**AI:** {msg['content'][:80]}...")

user_query = st.sidebar.chat_input("Ask about medicines...", key="ml_chat")
if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    response = st.session_state.medicine_search.answer_query(user_query)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()

# Main content
st.markdown("# 🧠 Knowledge Hub")
st.markdown("*Your AI-powered medicine information center*")
st.markdown("---")

# Search tabs
tab1, tab2 = st.tabs(["🔍 Medicine Search", "💬 Ask AI"])

with tab1:
    st.markdown("### Search Medicine Database")
    st.markdown("*Search from over 7,000 medicines to find detailed information*")
    
    # Search input
    search_col1, search_col2 = st.columns([4, 1])
    with search_col1:
        search_query = st.text_input(
            "Search for a medicine",
            placeholder="Type medicine name (e.g., Paracetamol, Amoxicillin, Aspirin...)",
            key="med_search"
        )
    with search_col2:
        st.write("")
        st.write("")
        search_btn = st.button("🔍 Search", use_container_width=True)
    
    # Quick search suggestions
    st.markdown("**Quick Searches:**")
    quick_col1, quick_col2, quick_col3, quick_col4, quick_col5 = st.columns(5)
    with quick_col1:
        if st.button("Paracetamol", key="q1"):
            search_query = "Paracetamol"
    with quick_col2:
        if st.button("Amoxicillin", key="q2"):
            search_query = "Amoxicillin"
    with quick_col3:
        if st.button("Azithromycin", key="q3"):
            search_query = "Azithromycin"
    with quick_col4:
        if st.button("Omeprazole", key="q4"):
            search_query = "Omeprazole"
    with quick_col5:
        if st.button("Metformin", key="q5"):
            search_query = "Metformin"
    
    st.markdown("---")
    
    # Search results
    if search_query:
        results = st.session_state.medicine_search.search_medicine(search_query, limit=5)
        
        if results:
            st.markdown(f"### Found {len(results)} result(s) for '{search_query}'")
            
            for med in results:
                with st.expander(f"💊 {med['name']} — Match: {med['match_score']}%", expanded=True):
                    # Header with key info
                    info_col1, info_col2, info_col3 = st.columns(3)
                    with info_col1:
                        st.metric("💰 Price", f"₹{med['price']}")
                    with info_col2:
                        st.metric("🏭 Manufacturer", med['manufacturer'][:20] + "..." if len(str(med['manufacturer'])) > 20 else med['manufacturer'])
                    with info_col3:
                        st.metric("📦 Pack Size", med['pack_size'])
                    
                    # Composition
                    st.markdown(f"""
                    <div class="info-section">
                        <div class="info-title">🧪 Salt Composition</div>
                        <div class="info-content">{med['salt_composition']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Description/Benefits
                    st.markdown(f"""
                    <div class="info-section">
                        <div class="info-title">📋 Description & Benefits</div>
                        <div class="info-content">{med['description'][:800]}{'...' if len(str(med['description'])) > 800 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Side Effects
                    side_effects = med['side_effects']
                    if side_effects and side_effects != 'No side effects listed':
                        effects_list = side_effects.split(',')
                        effects_html = "".join([f"<li>{e.strip()}</li>" for e in effects_list[:10]])
                        st.markdown(f"""
                        <div class="info-section" style="border-left-color: #ffcc00; background: rgba(255, 204, 0, 0.1);">
                            <div class="info-title" style="color: #ffcc00;">⚠️ Side Effects</div>
                            <div class="info-content">
                                <ul class="side-effects-list" style="margin: 0; padding-left: 1.5rem;">
                                    {effects_html}
                                </ul>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Drug Interactions
                    interactions = med['drug_interactions']
                    if interactions.get('drug') and len(interactions['drug']) > 0:
                        st.markdown(f"""
                        <div class="info-section interaction-warning">
                            <div class="info-title interaction-title">🔗 Drug Interactions</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for i, (drug, effect) in enumerate(zip(interactions['drug'][:5], interactions['effect'][:5])):
                            effect_color = "#ff4444" if "LIFE-THREATENING" in effect else "#ffcc00" if "SERIOUS" in effect else "#32CD32"
                            st.markdown(f"- **{drug}**: <span style='color: {effect_color};'>{effect}</span>", unsafe_allow_html=True)
                    
                    st.markdown("---")
        else:
            st.warning(f"No results found for '{search_query}'. Try a different search term.")

with tab2:
    st.markdown("### 💬 Ask the AI Assistant")
    st.markdown("*Ask natural language questions about medicines*")
    
    # Example questions
    st.markdown("**Try asking:**")
    example_col1, example_col2 = st.columns(2)
    with example_col1:
        if st.button("What are the side effects of Azithromycin?", key="ex1"):
            st.session_state.kb_chat_history.append({
                "role": "user",
                "content": "What are the side effects of Azithromycin?"
            })
            st.session_state.kb_chat_history.append({
                "role": "assistant",
                "content": st.session_state.medicine_search.answer_query("What are the side effects of Azithromycin?")
            })
            st.rerun()
    with example_col2:
        if st.button("Tell me about drug interactions of Paracetamol", key="ex2"):
            st.session_state.kb_chat_history.append({
                "role": "user",
                "content": "Tell me about drug interactions of Paracetamol"
            })
            st.session_state.kb_chat_history.append({
                "role": "assistant",
                "content": st.session_state.medicine_search.answer_query("Tell me about drug interactions of Paracetamol")
            })
            st.rerun()
    
    st.markdown("---")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for msg in st.session_state.kb_chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message-user">
                    <strong>You:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.container():
                    st.markdown("**🤖 AI Assistant:**")
                    st.markdown(msg['content'])
                    st.markdown("---")
    
    # Chat input
    user_input = st.chat_input("Ask a question about any medicine...", key="kb_chat_input")
    
    if user_input:
        # Add to history
        st.session_state.kb_chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get AI response
        response = st.session_state.medicine_search.answer_query(user_input)
        st.session_state.kb_chat_history.append({
            "role": "assistant",
            "content": response
        })
        
        st.rerun()
    
    # Clear chat button
    if st.session_state.kb_chat_history:
        if st.button("🗑️ Clear Chat", key="clear_kb_chat"):
            st.session_state.kb_chat_history = []
            st.rerun()

# Info section
st.markdown("---")
st.markdown("### ℹ️ About the Knowledge Hub")
st.info("""
**Data Source:** This knowledge hub contains information on over 7,000 medicines from a comprehensive medical database.

**Features:**
- 🔍 **Fuzzy Search:** Find medicines even with partial or misspelled names
- 📋 **Detailed Information:** Composition, description, side effects, and drug interactions
- 💬 **Natural Language:** Ask questions in plain English

**⚠️ Disclaimer:** This information is for educational purposes only. Always consult a healthcare professional before making medical decisions.
""")
