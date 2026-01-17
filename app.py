"""
Remidex - Smart Medication Management System
Main application entry point with sidebar navigation and AI chatbot
"""

import streamlit as st
import sys
import os

# Add utils to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import Database
from utils.ai_helper import get_medicine_search

# Page configuration
st.set_page_config(
    page_title="Remidex - Smart Medication Manager",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for theming
def inject_custom_css():
    st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --lime-green: #32CD32;
            --black: #000000;
            --white: #FFFFFF;
            --dark-gray: #1a1a1a;
        }
        
        /* Global styling */
        .stApp {
            background-color: var(--black);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: var(--dark-gray);
            border-right: 2px solid var(--lime-green);
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--lime-green) !important;
        }
        
        /* Lime green text class */
        .lime-text {
            color: var(--lime-green);
        }
        
        /* Big title styling */
        .big-title {
            font-size: 4rem;
            font-weight: 800;
            color: var(--lime-green);
            text-shadow: 0 0 20px rgba(50, 205, 50, 0.5);
            margin-bottom: 0;
            line-height: 1.1;
        }
        
        /* Quote styling */
        .health-quote {
            font-size: 1.2rem;
            font-style: italic;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 1rem;
            padding: 1rem;
            border-left: 4px solid var(--lime-green);
            background: rgba(50, 205, 50, 0.1);
        }
        
        /* Navigation card styling */
        .nav-card {
            background: linear-gradient(145deg, var(--dark-gray), #0d0d0d);
            border: 2px solid var(--lime-green);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        
        .nav-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(50, 205, 50, 0.3);
            background: linear-gradient(145deg, #1a1a1a, var(--dark-gray));
        }
        
        .nav-card-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .nav-card-title {
            color: var(--lime-green);
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(145deg, var(--lime-green), #28a428);
            color: var(--black) !important;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 2rem;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(50, 205, 50, 0.4);
        }
        
        /* Delete button (red) */
        .delete-btn > button {
            background: linear-gradient(145deg, #ff4444, #cc0000) !important;
            color: white !important;
        }
        
        /* Input styling */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div {
            background-color: var(--dark-gray) !important;
            border: 1px solid var(--lime-green) !important;
            color: var(--white) !important;
            border-radius: 8px !important;
        }
        
        /* Warning box */
        .warning-box {
            background: linear-gradient(145deg, #ff6b6b, #ee5a5a);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            color: white;
            font-weight: 500;
        }
        
        /* Success box */
        .success-box {
            background: linear-gradient(145deg, var(--lime-green), #28a428);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            color: var(--black);
            font-weight: 500;
        }
        
        /* Medicine card */
        .medicine-card {
            background: var(--dark-gray);
            border: 1px solid var(--lime-green);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* Chat styling */
        .stChatMessage {
            background-color: var(--dark-gray) !important;
            border-radius: 10px !important;
        }
        
        /* Divider */
        hr {
            border-color: var(--lime-green);
            opacity: 0.3;
        }
        
        /* Metric styling */
        [data-testid="stMetricValue"] {
            color: var(--lime-green) !important;
        }
        
        /* Checkbox styling */
        .stCheckbox label span {
            color: var(--white) !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: var(--dark-gray) !important;
            border-radius: 8px !important;
        }
        
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'db' not in st.session_state:
        st.session_state.db = Database()
    
    if 'medicine_search' not in st.session_state:
        st.session_state.medicine_search = get_medicine_search()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def render_sidebar_chatbot():
    """Render the AI chatbot in the sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 AI Assistant")
    st.sidebar.markdown("*Ask me about any medicine!*")
    
    # Display chat history (last 5 messages)
    for msg in st.session_state.chat_history[-5:]:
        if msg["role"] == "user":
            st.sidebar.markdown(f"**You:** {msg['content'][:50]}...")
        else:
            st.sidebar.markdown(f"**AI:** {msg['content'][:100]}...")
    
    # Chat input
    user_query = st.sidebar.chat_input("Ask about medicines...", key="sidebar_chat")
    
    if user_query:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query
        })
        
        # Get AI response
        response = st.session_state.medicine_search.answer_query(user_query)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Rerun to show response
        st.rerun()


def main():
    """Main application function"""
    # Initialize
    inject_custom_css()
    init_session_state()
    
    # Sidebar header
    st.sidebar.markdown("# 💊 Remidex")
    st.sidebar.markdown("*Your Smart Medication Manager*")
    st.sidebar.markdown("---")
    
    # Navigation info
    st.sidebar.markdown("### 📍 Navigation")
    st.sidebar.markdown("Use the pages menu above to navigate.")
    
    # Render chatbot at bottom of sidebar
    render_sidebar_chatbot()
    
    # Main page content (Home)
    col1, col2 = st.columns([6, 4])
    
    with col1:
        st.markdown('<p class="big-title">Remidex</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 1.5rem; color: #32CD32;">Smart Medication Management System</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="health-quote">
            "Healing is a matter of time, but it is sometimes also a matter of opportunity."
            <br><span style="float: right; font-size: 0.9rem;">— Hippocrates</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">
            Welcome to <strong style="color: #32CD32;">Remidex</strong> - your personal medication companion. 
            Track your medicines, manage supplies, set reminders, and get AI-powered insights 
            about your medications.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Navigation cards
        nav_items = [
            ("💊", "Add Medicine", "Schedule your medications", "2_💊_Add_Medicine"),
            ("📦", "Medicine Supply", "Track your stock", "3_📦_Medicine_Supply"),
            ("🧠", "Knowledge Hub", "AI-powered insights", "4_🧠_ML_Agent"),
            ("📜", "History & Log", "View your records", "5_📜_History"),
        ]
        
        for icon, title, desc, page in nav_items:
            st.markdown(f"""
            <div class="nav-card">
                <div class="nav-card-icon">{icon}</div>
                <p class="nav-card-title">{title}</p>
                <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin: 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.5); font-size: 0.9rem;">
        Made with ❤️ for better health management | Remidex © 2026
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
