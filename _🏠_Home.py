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

# Page configuration
st.set_page_config(
    page_title="Home | Remidex",
    page_icon="🏠",
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
    
    .big-title {
        font-size: 4.5rem;
        font-weight: 800;
        color: var(--lime-green);
        text-shadow: 0 0 30px rgba(50, 205, 50, 0.5);
        margin-bottom: 0;
        line-height: 1.1;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(50, 205, 50, 0.5); }
        to { text-shadow: 0 0 40px rgba(50, 205, 50, 0.8); }
    }
    
    .health-quote {
        font-size: 1.3rem;
        font-style: italic;
        color: rgba(255, 255, 255, 0.85);
        margin-top: 1.5rem;
        padding: 1.5rem;
        border-left: 5px solid var(--lime-green);
        background: linear-gradient(90deg, rgba(50, 205, 50, 0.15), transparent);
        border-radius: 0 10px 10px 0;
    }
    
    .nav-card {
        background: linear-gradient(145deg, var(--dark-gray), #0d0d0d);
        border: 2px solid var(--lime-green);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .nav-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(50, 205, 50, 0.3);
    }
    
    .nav-card-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .nav-card-title {
        color: var(--lime-green);
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .nav-card-desc {
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
        margin: 0;
    }
    
    .subtitle {
        font-size: 1.5rem;
        color: var(--lime-green);
        font-weight: 500;
        margin-top: -10px;
    }
    
    .welcome-text {
        color: rgba(255,255,255,0.85);
        font-size: 1.15rem;
        line-height: 1.8;
        margin-top: 2rem;
    }
    
    .feature-badge {
        display: inline-block;
        background: var(--lime-green);
        color: var(--black);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--dark-gray);
        border-right: 2px solid var(--lime-green);
    }
    
    h1, h2, h3 { color: var(--lime-green) !important; }
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
st.sidebar.markdown("# 💊 Remidex")
st.sidebar.markdown("*Your Smart Medication Manager*")
st.sidebar.markdown("---")

# Sidebar AI Chatbot
st.sidebar.markdown("### 🤖 AI Assistant")
st.sidebar.markdown("*Ask me about any medicine!*")

for msg in st.session_state.chat_history[-3:]:
    if msg["role"] == "user":
        st.sidebar.markdown(f"**You:** {msg['content'][:40]}...")
    else:
        st.sidebar.markdown(f"**AI:** {msg['content'][:80]}...")

user_query = st.sidebar.chat_input("Ask about medicines...", key="home_chat")
if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    response = st.session_state.medicine_search.answer_query(user_query)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()

# Main content
col1, col2 = st.columns([6, 4])

with col1:
    st.markdown('<p class="big-title">Remidex</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Smart Medication Management System</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="health-quote">
        "Healing is a matter of time, but it is sometimes also a matter of opportunity."
        <br><span style="float: right; font-size: 0.95rem; margin-top: 0.5rem;">— Hippocrates</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="welcome-text">
        Welcome to <strong style="color: #32CD32;">Remidex</strong> — your personal medication companion. 
        Take control of your health with our comprehensive medication management system.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div>
        <span class="feature-badge">📅 Schedule Alerts</span>
        <span class="feature-badge">📦 Track Supply</span>
        <span class="feature-badge">🧠 AI Insights</span>
        <span class="feature-badge">📜 History Log</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation cards as actual buttons
    st.markdown("""
    <div class="nav-card">
        <div class="nav-card-icon">💊</div>
        <p class="nav-card-title">Add Medicine</p>
        <p class="nav-card-desc">Schedule your medications & set alerts</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Add Medicine", key="nav_add", use_container_width=True):
        st.switch_page("pages/2_💊_Add_Medicine.py")
    
    st.markdown("""
    <div class="nav-card">
        <div class="nav-card-icon">📦</div>
        <p class="nav-card-title">Medicine Supply</p>
        <p class="nav-card-desc">Track stock & get low supply alerts</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Supply Tracker", key="nav_supply", use_container_width=True):
        st.switch_page("pages/3_📦_Medicine_Supply.py")
    
    st.markdown("""
    <div class="nav-card">
        <div class="nav-card-icon">🧠</div>
        <p class="nav-card-title">Knowledge Hub</p>
        <p class="nav-card-desc">AI-powered medicine insights</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Knowledge Hub", key="nav_ml", use_container_width=True):
        st.switch_page("pages/4_🧠_ML_Agent.py")
    
    st.markdown("""
    <div class="nav-card">
        <div class="nav-card-icon">📜</div>
        <p class="nav-card-title">History & Log</p>
        <p class="nav-card-desc">View medication history & daily log</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to History", key="nav_history", use_container_width=True):
        st.switch_page("pages/5_📜_History.py")

# Quick stats
st.markdown("---")
st.markdown("### 📊 Quick Stats")

stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

medicines = st.session_state.db.get_all_medicines()
supplies = st.session_state.db.get_all_supplies()
history = st.session_state.db.get_today_history()

with stats_col1:
    st.metric("💊 Scheduled Medicines", len(medicines))

with stats_col2:
    st.metric("📦 Tracked Supplies", len(supplies))

with stats_col3:
    st.metric("✅ Taken Today", len(history))

with stats_col4:
    # Count low stock items
    low_stock = 0
    for supply in supplies:
        if supply['daily_dosage'] > 0:
            days_left = supply['current_stock'] / supply['daily_dosage']
            if days_left <= supply['alert_threshold']:
                low_stock += 1
    st.metric("⚠️ Low Stock Alerts", low_stock)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: rgba(255,255,255,0.5); font-size: 0.9rem; padding: 1rem;">
    Made with ❤️ for better health management | <strong style="color: #32CD32;">Remidex</strong> © 2026
</div>
""", unsafe_allow_html=True)
