"""
Authentication Utility for Remidex
"""
import streamlit as st
import time
from utils.database import Database

def require_auth():
    """
    Check if user is authenticated. 
    If not, show login/register screen and stop execution.
    Returns True if authenticated.
    """
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if st.session_state.authenticated:
        return True
        
    # Initialize DB if needed (for auth checks)
    if 'db' not in st.session_state:
        st.session_state.db = Database()
        st.session_state.db._init_db()

    # Show Login Screen
    st.markdown("""
    <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        .main-header {
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #10B981, #3B82F6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="main-header">RemideX</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Log In", use_container_width=True)
                
                if submit:
                    user_id = st.session_state.db.verify_user(username, password)
                    if user_id:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success("Welcome back!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                        
        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                reg_submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if reg_submit:
                    if new_pass != confirm_pass:
                        st.error("Passwords do not match")
                    elif len(new_pass) < 4:
                        st.error("Password must be at least 4 characters")
                    else:
                        success = st.session_state.db.create_user(new_user, new_pass)
                        if success:
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username already taken.")

    # Stop execution of the rest of the page if not authenticated
    st.stop()
    return False

def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()
