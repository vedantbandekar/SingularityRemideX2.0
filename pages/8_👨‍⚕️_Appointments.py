"""
Remidex - Doctor Appointments Page
Manage upcoming doctor visits and history
"""

import streamlit as st
import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import Database
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Appointments | Remidex",
    page_icon="👨‍⚕️",
    layout="wide"
)

# Inject premium CSS
inject_css(st)

# Additional CSS
st.markdown("""
<style>
    .appt-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .appt-card:hover {
        border-color: var(--primary-light);
        transform: translateY(-3px);
    }
    
    .appt-card.past {
        opacity: 0.7;
        border-color: rgba(255,255,255,0.05);
    }
    
    .doctor-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--primary-light);
        margin-bottom: 0.25rem;
    }
    
    .specialty-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        color: var(--accent);
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    .date-box {
        background: rgba(0,0,0,0.3);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        text-align: center;
        width: fit-content;
    }
    
    .date-day {
        font-size: 1.5rem;
        font-weight: 800;
        line-height: 1;
        color: var(--text-primary);
    }
    
    .date-month {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: var(--text-secondary);
    }
    
    .time-text {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .countdown-tag {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: var(--warning);
        color: #000;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
if 'db' not in st.session_state:
    st.session_state.db = Database()

# Sidebar
from utils.sidebar import render_ai_sidebar

render_ai_sidebar()
st.sidebar.markdown("### 🗓️ Agenda")
st.sidebar.info("Keep track of all your medical visits in one place.")

# Main content
st.markdown('<h1 class="page-header">👨‍⚕️ Doctor Appointments</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Schedule and view your upcoming medical visits</p>', unsafe_allow_html=True)
st.markdown("---")

# SECTION 1: ADD APPOINTMENT
st.markdown('<p class="section-title">📅 Schedule New Visit</p>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    with st.form("add_appt_form", clear_on_submit=True):
        
        col1, col2 = st.columns(2)
        with col1:
            doctor_name = st.text_input("Doctor Name", placeholder="e.g. Dr. House")
            specialty = st.text_input("Specialty", placeholder="e.g. Cardiologist")
        
        with col2:
            appt_date = st.date_input("Date", date.today() + timedelta(days=1))
            appt_time = st.time_input("Time", datetime.now().time())
            
        reason = st.text_input("Reason for Visit", placeholder="e.g. Annual checkup, Follow-up...")
        notes = st.text_area("Notes to self", placeholder="Bring MRI results, Fast for 12 hours...")
        
        submitted = st.form_submit_button("🗓️ Schedule Appointment", use_container_width=True)
        
        if submitted:
            if doctor_name and appt_date:
                st.session_state.db.add_appointment(
                    doctor_name,
                    specialty,
                    appt_date.isoformat(),
                    appt_time.strftime("%H:%M"),
                    reason,
                    notes
                )
                st.success(f"✅ Appointment scheduled with {doctor_name}")
                st.rerun()
            else:
                st.error("Please enter doctor name and date.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# SECTION 2: LIST APPOINTMENTS
st.markdown('<div style="display:flex; justify_content:space-between; align-items:center;">'
            '<p class="section-title">🏥 Your Visits</p>'
            '</div>', unsafe_allow_html=True)

appts = st.session_state.db.get_all_appointments()

if not appts:
    st.info("No appointments scheduled.")
else:
    # Separate upcoming and past
    today = date.today().isoformat()
    now_time = datetime.now().strftime("%H:%M")
    
    upcoming = []
    past = []
    
    for a in appts:
        is_past = False
        if a['appt_date'] < today:
            is_past = True
        elif a['appt_date'] == today and a['appt_time'] < now_time:
            is_past = True
            
        if is_past:
            past.append(a)
        else:
            upcoming.append(a)
            
    # Display Upcoming
    if upcoming:
        st.markdown("#### 🔜 Upcoming")
        for appt in upcoming:
            
            # Date formatting
            d_obj = datetime.strptime(appt['appt_date'], "%Y-%m-%d")
            day_str = d_obj.strftime("%d")
            month_str = d_obj.strftime("%b")
            day_name = d_obj.strftime("%A")
            
            # Days remaining
            delta = d_obj.date() - date.today()
            days_until = delta.days
            if days_until == 0:
                tag = "TODAY"
            elif days_until == 1:
                tag = "TOMORROW"
            else:
                tag = f"IN {days_until} DAYS"
            
            # Prepare optional notes HTML
            notes_content = appt['notes'] if (appt['notes'] and appt['notes'].strip()) else "No notes added."
            notes_html = f'<div style="font-size:0.9rem; margin-top:0.25rem; font-style:italic; color:var(--text-secondary);">📝 {notes_content}</div>'
            
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div class="appt-card">
                    <span class="countdown-tag">{tag}</span>
                    <div style="display:flex; gap: 1.5rem; align-items: flex-start;">
                        <div class="date-box">
                            <div class="date-month">{month_str}</div>
                            <div class="date-day">{day_str}</div>
                        </div>
                        <div>
                            <div class="doctor_name">🩺 {appt['doctor_name']}</div>
                            <span class="specialty-badge">{appt['specialty']}</span>
                            <div class="time-text">🕒 {appt['appt_time']} • {day_name}</div>
                            <div style="color: var(--text-secondary); margin-top: 0.5rem;">
                                <strong>Reason:</strong> {appt['reason']}
                            </div>
                            {notes_html}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_appt_{appt['id']}", type="secondary", help="Cancel appointment"):
                    st.session_state.db.delete_appointment(appt['id'])
                    st.rerun()

    # Display Past
    if past:
        with st.expander("Show Past Appointments"):
            st.markdown("#### 📜 History")
            for appt in sorted(past, key=lambda x: x['appt_date'], reverse=True):
                 col1, col2 = st.columns([5, 1])
                 with col1:
                    st.markdown(f"""
                    <div class="appt-card past">
                        <div style="display:flex; gap: 1rem; align-items: center;">
                            <div style="font-weight:bold; color:var(--text-secondary);">{appt['appt_date']}</div>
                            <div style="border-left: 2px solid var(--glass-border); padding-left: 1rem;">
                                <div style="font-weight:bold;">{appt['doctor_name']} ({appt['specialty']})</div>
                                <div style="font-size:0.9rem; color:var(--text-secondary);">{appt['reason']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                 with col2:
                    if st.button("🗑️", key=f"del_past_{appt['id']}", type="secondary"):
                        st.session_state.db.delete_appointment(appt['id'])
                        st.rerun()

render_footer(st)
