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
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Add Medicine | Remidex",
    page_icon="💊",
    layout="wide"
)

# Inject premium CSS
inject_css(st)

# Additional page-specific CSS
st.markdown("""
<style>
    [data-testid="stForm"] {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .alert-time-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: var(--text-primary);
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
    }
    
    .tip-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.25rem;
        transition: all 0.3s ease;
    }
    
    .tip-card:hover {
        border-color: var(--primary-light);
        transform: translateY(-3px);
    }
    
    .tip-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .tip-title {
        color: var(--accent);
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    .tip-text {
        color: var(--text-secondary);
        font-size: 0.85rem;
        line-height: 1.5;
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
from utils.sidebar import render_ai_sidebar

render_ai_sidebar()

# Main content
st.markdown('<h1 class="page-header">💊 Add Medicine</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Schedule your medications and set reminder alerts</p>', unsafe_allow_html=True)
st.markdown("---")

# SECTION 1: ADD MEDICINE FORM
st.markdown('<p class="section-title">➕ Add New Medicine</p>', unsafe_allow_html=True)

with st.container():

    with st.form("add_medicine_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            medicine_name = st.text_input("Medicine Name", placeholder="Enter medicine name...")
        with col2:
            dosage = st.text_input("Dosage", placeholder="e.g., 500mg")
        
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
        
        alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)
        
        with alert_col1:
            time1 = st.time_input("Morning", value=time(8, 0), key="time1")
            add_time1 = st.checkbox("Enable", key="check1")
        
        with alert_col2:
            time2 = st.time_input("Afternoon", value=time(14, 0), key="time2")
            add_time2 = st.checkbox("Enable", key="check2")
        
        with alert_col3:
            time3 = st.time_input("Evening", value=time(20, 0), key="time3")
            add_time3 = st.checkbox("Enable", key="check3")
        
        with alert_col4:
            custom_time = st.time_input("Custom", value=time(22, 0), key="custom_time")
            add_custom = st.checkbox("Enable", key="check_custom")
        
        st.markdown("<br>", unsafe_allow_html=True)
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


st.markdown("---")

# SECTION 2: SCHEDULED MEDICINES LIST
st.markdown('<p class="section-title">📋 Scheduled Medicines</p>', unsafe_allow_html=True)

medicines = st.session_state.db.get_all_medicines()

if not medicines:
    st.markdown("""
    <div class="info-box">
        📝 No medicines scheduled yet. Add your first medicine above to get started!
    </div>
    """, unsafe_allow_html=True)
else:
    # Grid layout for medicines
    for i in range(0, len(medicines), 2):
        col1, col2 = st.columns(2)
        
        # First card
        with col1:
            med = medicines[i]
            st.markdown(f"""
            <div class="medicine-card">
                <div class="medicine-name">💊 {med['name']}</div>
                <div class="medicine-info"><strong>Dosage:</strong> {med['dosage']}</div>
                <div class="medicine-info"><strong>Frequency:</strong> {med['frequency']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Alerts & Actions
            act_col1, act_col2 = st.columns([3, 1])
            with act_col1:
                if med['alert_times']:
                    alert_html = "".join([f'<span class="alert-time-badge">🔔 {t}</span>' for t in med['alert_times']])
                    st.markdown(f"{alert_html}", unsafe_allow_html=True)
                else:
                    st.markdown("*No alerts*")
            with act_col2:
                 if st.button(f"🗑️", key=f"del_{med['id']}", help="Delete medicine"):
                    st.session_state.db.delete_medicine(med['id'])
                    st.rerun()
        
        # Second card (if exists)
        if i + 1 < len(medicines):
            with col2:
                med = medicines[i+1]
                st.markdown(f"""
                <div class="medicine-card">
                    <div class="medicine-name">💊 {med['name']}</div>
                    <div class="medicine-info"><strong>Dosage:</strong> {med['dosage']}</div>
                    <div class="medicine-info"><strong>Frequency:</strong> {med['frequency']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Alerts & Actions
                act_col1, act_col2 = st.columns([3, 1])
                with act_col1:
                    if med['alert_times']:
                        alert_html = "".join([f'<span class="alert-time-badge">🔔 {t}</span>' for t in med['alert_times']])
                        st.markdown(f"{alert_html}", unsafe_allow_html=True)
                    else:
                        st.markdown("*No alerts*")
                with act_col2:
                     if st.button(f"🗑️", key=f"del_{med['id']}", help="Delete medicine"):
                        st.session_state.db.delete_medicine(med['id'])
                        st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)

# Tips section
st.markdown("---")
st.markdown('<p class="section-title">💡 Tips</p>', unsafe_allow_html=True)
tips_col1, tips_col2, tips_col3 = st.columns(3)

with tips_col1:
    st.markdown("""
    <div class="tip-card">
        <div class="tip-icon">🔔</div>
        <div class="tip-title">Set Multiple Alerts</div>
        <div class="tip-text">Add alerts for each time you need to take your medication for better adherence.</div>
    </div>
    """, unsafe_allow_html=True)

with tips_col2:
    st.markdown("""
    <div class="tip-card">
        <div class="tip-icon">📦</div>
        <div class="tip-title">Track Your Supply</div>
        <div class="tip-text">Don't forget to add your medicine to Supply Tracker to monitor stock levels.</div>
    </div>
    """, unsafe_allow_html=True)

with tips_col3:
    st.markdown("""
    <div class="tip-card">
        <div class="tip-icon">✅</div>
        <div class="tip-title">Log Daily</div>
        <div class="tip-text">Mark medicines as taken in the History page to keep accurate health records.</div>
    </div>
    """, unsafe_allow_html=True)

# Footer
render_footer(st)
