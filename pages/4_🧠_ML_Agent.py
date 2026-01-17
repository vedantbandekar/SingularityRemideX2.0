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
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Knowledge Hub | Remidex",
    page_icon="🧠",
    layout="wide"
)

# Inject premium CSS
inject_css(st)

# Additional page-specific CSS
st.markdown("""
<style>
    .search-container {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .result-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        border-color: var(--primary-light);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15);
    }
    
    .medicine-title {
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.75rem;
    }
    
    .info-section {
        background: rgba(99, 102, 241, 0.1);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border-left: 4px solid var(--primary);
    }
    
    .info-title {
        color: var(--primary-light);
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .info-content {
        color: var(--text-secondary);
        line-height: 1.7;
        font-size: 0.95rem;
    }
    
    .side-effects-section {
        background: rgba(245, 158, 11, 0.1);
        border-left-color: var(--warning);
    }
    
    .side-effects-section .info-title {
        color: var(--warning);
    }
    
    .interaction-section {
        background: rgba(239, 68, 68, 0.1);
        border-left-color: var(--danger);
    }
    
    .interaction-section .info-title {
        color: #F87171;
    }
    
    .match-score {
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: var(--text-primary);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
    }
    
    .quick-btn {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
    }
    
    .quick-btn:hover {
        border-color: var(--primary) !important;
        background: var(--bg-elevated) !important;
    }
    
    .chat-message-user {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: var(--text-primary);
        padding: 1rem 1.25rem;
        border-radius: 16px 16px 4px 16px;
        margin: 0.75rem 0;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .chat-message-ai {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        padding: 1rem 1.25rem;
        border-radius: 16px 16px 16px 4px;
        margin: 0.75rem 0;
        color: var(--text-primary);
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }
    
    .about-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
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
from utils.sidebar import render_ai_sidebar

render_ai_sidebar()

# Main content
st.markdown('<h1 class="page-header">🧠 Knowledge Hub</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Your AI-powered medicine information center</p>', unsafe_allow_html=True)
st.markdown("---")

st.markdown('<p class="section-title">Search Medicine Database</p>', unsafe_allow_html=True)
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
                    effects_list = []
                    if isinstance(side_effects, list):
                        effects_list = side_effects
                    elif isinstance(side_effects, str):
                        effects_list = side_effects.split(',')
                    
                    if effects_list:
                        effects_html = "".join([f"<li>{str(e).strip()}</li>" for e in effects_list[:10]])
                        st.markdown(f"""
                        <div class="info-section side-effects-section">
                            <div class="info-title">⚠️ Side Effects</div>
                            <div class="info-content">
                                <ul style="margin: 0; padding-left: 1.5rem; color: var(--warning);">
                                    {effects_html}
                                </ul>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Drug Interactions
                interactions = med['drug_interactions']
                # Check for dict structure
                if isinstance(interactions, dict) and interactions.get('drug') and len(interactions['drug']) > 0:
                    st.markdown("""
                    <div class="info-section interaction-section">
                        <div class="info-title">🔗 Drug Interactions</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, (drug, effect) in enumerate(zip(interactions['drug'][:5], interactions['effect'][:5])):
                        effect_color = "#EF4444" if "LIFE-THREATENING" in effect else "#F59E0B" if "SERIOUS" in effect else "#10B981"
                        st.markdown(f"- **{drug}**: <span style='color: {effect_color};'>{effect}</span>", unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.warning(f"No results found for '{search_query}'. Try a different search term.")

# Info section
# Info section
st.markdown("---")
st.markdown('<p class="section-title">ℹ️ About the Knowledge Hub</p>', unsafe_allow_html=True)

st.markdown("""
<div class="about-card">
    <p style="color: var(--text-primary); font-weight: 600; margin-bottom: 1rem;">📊 Data Source</p>
    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
        This knowledge hub contains information on over 7,000 medicines from a comprehensive medical database.
    </p>
    <p style="color: var(--text-primary); font-weight: 600; margin-bottom: 0.75rem;">✨ Features</p>
    <ul style="color: var(--text-secondary); margin-bottom: 1.5rem; padding-left: 1.5rem;">
        <li><strong style="color: var(--primary);">Fuzzy Search:</strong> Find medicines even with partial or misspelled names</li>
        <li><strong style="color: var(--primary);">Detailed Information:</strong> Composition, description, side effects, and drug interactions</li>
        <li><strong style="color: var(--primary);">Natural Language:</strong> Ask questions in plain English</li>
    </ul>
    <p style="color: var(--warning); font-size: 0.9rem;">
        ⚠️ <strong>Disclaimer:</strong> This information is for educational purposes only. Always consult a healthcare professional before making medical decisions.
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
render_footer(st)
