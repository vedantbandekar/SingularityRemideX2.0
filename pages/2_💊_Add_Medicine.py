"""
Remidex - Add Medicine Page
Form to add medicines with scheduling and alert times
"""

import streamlit as st
import sys
import os
from datetime import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import Database
from utils.ai_helper import get_medicine_search

# Page configuration
st.set_page_config(
    page_title="Add Medicine | Remidex",
    page_icon="💊",
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
    
    .medicine-card {
        background: linear-gradient(145deg, var(--dark-gray), #0d0d0d);
        border: 1px solid var(--lime-green);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
    }
    
    .medicine-name {
        color: var(--lime-green);
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .medicine-detail {
        color: rgba(255,255,255,0.8);
        font-size: 0.95rem;
        margin: 0.3rem 0;
    }
    
    .alert-time-badge {
        display: inline-block;
        background: var(--lime-green);
        color: var(--black);
        padding: 0.25rem 0.6rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .form-section {
        background: var(--dark-gray);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(50, 205, 50, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(145deg, var(--lime-green), #28a428);
        color: var(--black) !important;
        font-weight: 600;
        border: none;
        border-radius: 10px;
    }
    
    .delete-btn button {
        background: linear-gradient(145deg, #ff4444, #cc0000) !important;
        color: white !important;
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
if 'alert_times' not in st.session_state:
    st.session_state.alert_times = []

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

user_query = st.sidebar.chat_input("Ask about medicines...", key="add_med_chat")
if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    response = st.session_state.medicine_search.answer_query(user_query)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()

# Main content
st.markdown("# 💊 Add Medicine")
st.markdown("*Schedule your medications and set reminder alerts*")
st.markdown("---")

# Form and list columns
form_col, list_col = st.columns([1, 1])

with form_col:
    st.markdown("### ➕ Add New Medicine")
    
    with st.form("add_medicine_form", clear_on_submit=True):
        medicine_name = st.text_input("Medicine Name", placeholder="Enter medicine name...")
        
        col_dosage, col_freq = st.columns(2)
        with col_dosage:
            dosage = st.text_input("Dosage", placeholder="e.g., 500mg")
        with col_freq:
            frequency = st.selectbox("Frequency", [
                "Once Daily",
                "Twice Daily",
                "Three Times Daily",
                "Four Times Daily",
                "Every 6 Hours",
                "Every 8 Hours",
                "Every 12 Hours",
                "As Needed",
                "Weekly",
                "Custom"
            ])
        
        st.markdown("---")
        st.markdown("#### ⏰ Alert Times")
        st.markdown("*Add specific times for medication reminders*")
        
        alert_col1, alert_col2, alert_col3 = st.columns(3)
        
        with alert_col1:
            time1 = st.time_input("Morning", value=time(8, 0), key="time1")
            add_time1 = st.checkbox("Add morning alert", key="check1")
        
        with alert_col2:
            time2 = st.time_input("Afternoon", value=time(14, 0), key="time2")
            add_time2 = st.checkbox("Add afternoon alert", key="check2")
        
        with alert_col3:
            time3 = st.time_input("Evening", value=time(20, 0), key="time3")
            add_time3 = st.checkbox("Add evening alert", key="check3")
        
        # Custom time input
        st.markdown("**Custom Time:**")
        custom_col1, custom_col2 = st.columns([2, 1])
        with custom_col1:
            custom_time = st.time_input("Select time", value=time(12, 0), key="custom_time")
        with custom_col2:
            add_custom = st.checkbox("Add custom", key="check_custom")
        
        submitted = st.form_submit_button("💊 Add Medicine", use_container_width=True)
        
        if submitted:
            if medicine_name and dosage:
                # Add medicine to database
                med_id = st.session_state.db.add_medicine(medicine_name, dosage, frequency)
                
                # Add selected alert times
                alerts_added = 0
                if add_time1:
                    st.session_state.db.add_alert(med_id, time1.strftime("%H:%M"))
                    alerts_added += 1
                if add_time2:
                    st.session_state.db.add_alert(med_id, time2.strftime("%H:%M"))
                    alerts_added += 1
                if add_time3:
                    st.session_state.db.add_alert(med_id, time3.strftime("%H:%M"))
                    alerts_added += 1
                if add_custom:
                    st.session_state.db.add_alert(med_id, custom_time.strftime("%H:%M"))
                    alerts_added += 1
                
                st.success(f"✅ Added **{medicine_name}** with {alerts_added} alert(s)!")
                st.rerun()
            else:
                st.error("Please fill in medicine name and dosage.")

with list_col:
    st.markdown("### 📋 Scheduled Medicines")
    
    medicines = st.session_state.db.get_all_medicines()
    
    if not medicines:
        st.info("No medicines scheduled yet. Add your first medicine!")
    else:
        for med in medicines:
            with st.container():
                st.markdown(f"""
                <div class="medicine-card">
                    <div class="medicine-name">💊 {med['name']}</div>
                    <div class="medicine-detail"><strong>Dosage:</strong> {med['dosage']}</div>
                    <div class="medicine-detail"><strong>Frequency:</strong> {med['frequency']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display alert times
                if med['alert_times']:
                    alert_html = "".join([f'<span class="alert-time-badge">🔔 {t}</span>' for t in med['alert_times']])
                    st.markdown(f"**Alerts:** {alert_html}", unsafe_allow_html=True)
                else:
                    st.markdown("*No alerts set*")
                
                # Delete button
                if st.button(f"🗑️ Delete", key=f"del_{med['id']}", type="secondary"):
                    st.session_state.db.delete_medicine(med['id'])
                    st.success(f"Deleted {med['name']}")
                    st.rerun()
                
                st.markdown("---")

# Quick tips
st.markdown("---")
st.markdown("### 💡 Tips")
tips_col1, tips_col2, tips_col3 = st.columns(3)

with tips_col1:
    st.info("🔔 **Set Multiple Alerts** - Add alerts for each time you need to take your medication.")

with tips_col2:
    st.info("📦 **Track Supply** - Don't forget to add your medicine to Supply Tracker to monitor stock levels.")

with tips_col3:
    st.info("✅ **Log Daily** - Mark medicines as taken in the History page to keep accurate records.")
