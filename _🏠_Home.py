"""
Remidex - Smart Medication Management System
Main application entry point - Home Page
"""

import streamlit as st
import sys
import os
from datetime import date, timedelta

# Add utils to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import Database
from utils.ai_helper import get_medicine_search
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Remidex | Smart Medication Manager",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject premium CSS
inject_css(st)

# Additional Home page specific CSS
st.markdown("""
<style>
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--text-primary), var(--primary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    .quote-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(34, 211, 238, 0.1));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid var(--accent);
        border-radius: 0 16px 16px 0;
        padding: 1.5rem 2rem;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }
    
    .quote-text {
        font-size: 1.1rem;
        font-style: italic;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    .quote-author {
        font-size: 0.9rem;
        color: var(--primary-light);
        margin-top: 0.5rem;
        font-weight: 600;
    }
    
    .welcome-text {
        font-size: 1.1rem;
        line-height: 1.7;
        color: var(--text-secondary);
        margin-bottom: 2rem;
    }
    
    .welcome-text strong {
        color: var(--primary-light);
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

# Sidebar
render_sidebar_header(st)

# Sidebar AI Chatbot
st.sidebar.markdown("### 🤖 AI Assistant")
st.sidebar.markdown("*Ask me about any medicine!*")

# Scrollable chat container
with st.sidebar.container(height=400):
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")
            st.markdown("---")

user_query = st.sidebar.chat_input("Ask about medicines...", key="home_chat")
if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    response = st.session_state.medicine_search.answer_query(user_query)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()

# Main content
st.markdown('<h1 class="hero-title">Remidex</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Smart Medication Management System</p>', unsafe_allow_html=True)

st.markdown("""
<div class="quote-card">
    <p class="quote-text">"Healing is a matter of time, but it is sometimes also a matter of opportunity."</p>
    <p class="quote-author">— Hippocrates</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<p class="welcome-text">
    Welcome to <strong>Remidex</strong> — your personal medication companion. 
    Take control of your health with our comprehensive medication management system 
    powered by AI-driven insights. Track your medicines, manage supplies, and never miss a dose.
</p>
""", unsafe_allow_html=True)

st.markdown("### Features")
st.markdown("""
<div>
    <span class="feature-badge">📅 Smart Scheduling</span>
    <span class="feature-badge">📦 Supply Tracking</span>
    <span class="feature-badge">🧠 AI Knowledge Hub</span>
    <span class="feature-badge">📜 Detailed History</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Navigation Hub
st.markdown("### 🧭 Quick Navigation")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    st.markdown("""
    <div class="nav-card" style="min-height: 220px;">
        <div class="nav-card-icon">💊</div>
        <p class="nav-card-title">Add Medicine</p>
        <p class="nav-card-desc">Schedule & Alerts</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Add Medicine", key="nav_add", use_container_width=True):
        st.switch_page("pages/2_💊_Add_Medicine.py")

with nav_col2:
    st.markdown("""
    <div class="nav-card" style="min-height: 220px;">
        <div class="nav-card-icon">📦</div>
        <p class="nav-card-title">Supply Tracker</p>
        <p class="nav-card-desc">Stock & Low Alerts</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Manage Supply", key="nav_supply", use_container_width=True):
        st.switch_page("pages/3_📦_Medicine_Supply.py")

with nav_col3:
    st.markdown("""
    <div class="nav-card" style="min-height: 220px;">
        <div class="nav-card-icon">🧠</div>
        <p class="nav-card-title">Knowledge Hub</p>
        <p class="nav-card-desc">AI Insights & Info</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ask AI", key="nav_ml", use_container_width=True):
        st.switch_page("pages/4_🧠_ML_Agent.py")

with nav_col4:
    st.markdown("""
    <div class="nav-card" style="min-height: 220px;">
        <div class="nav-card-icon">📜</div>
        <p class="nav-card-title">History & Log</p>
        <p class="nav-card-desc">View Logs & Stats</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View History", key="nav_history", use_container_width=True):
        st.switch_page("pages/5_📜_History.py")

# Quick stats
st.markdown("---")
st.markdown('<p class="page-header" style="font-size: 1.5rem;">📊 Dashboard Overview</p>', unsafe_allow_html=True)

stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

medicines = st.session_state.db.get_all_medicines()
supplies = st.session_state.db.get_all_supplies()
history = st.session_state.db.get_today_history()

with stats_col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(medicines)}</div>
        <div class="stat-label">Scheduled Medicines</div>
    </div>
    """, unsafe_allow_html=True)

with stats_col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(supplies)}</div>
        <div class="stat-label">Tracked Supplies</div>
    </div>
    """, unsafe_allow_html=True)

with stats_col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(history)}</div>
        <div class="stat-label">Taken Today</div>
    </div>
    """, unsafe_allow_html=True)

with stats_col4:
    # Count low stock items
    low_stock = 0
    for supply in supplies:
        if supply['daily_dosage'] > 0:
            days_left = supply['current_stock'] / supply['daily_dosage']
            if days_left <= supply['alert_threshold']:
                low_stock += 1
    
    st.markdown(f"""
    <div class="stat-card" style="border-color: {'var(--danger)' if low_stock > 0 else 'var(--glass-border)'};">
        <div class="stat-value" style="color: {'var(--danger)' if low_stock > 0 else 'inherit'}; background: none; -webkit-text-fill-color: {'var(--danger)' if low_stock > 0 else 'var(--text-primary)'};">{low_stock}</div>
        <div class="stat-label">Low Stock Alerts</div>
    </div>
    """, unsafe_allow_html=True)

# Footer
render_footer(st)
