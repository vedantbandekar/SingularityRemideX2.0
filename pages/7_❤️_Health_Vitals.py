"""
Remidex - Health Vitals Page
Track regular health metrics like Blood Pressure, Sugar, and Weight
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import date, datetime, time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import Database
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Health Vitals | Remidex",
    page_icon="❤️",
    layout="wide"
)

# Inject premium CSS
inject_css(st)

# Additional CSS
st.markdown("""
<style>
    .vital-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .vital-card:hover {
        border-color: var(--primary-light);
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }
    
    .vital-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .vital-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .vital-unit {
        font-size: 1rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-left: 0.25rem;
    }
    
    .chart-container {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid var(--glass-border);
    }
</style>
""", unsafe_allow_html=True)

# Initialize
if 'db' not in st.session_state:
    st.session_state.db = Database()

# Ensure tables are created (in case of hot reload updates)
st.session_state.db._init_db()

# Sidebar
from utils.sidebar import render_ai_sidebar

render_ai_sidebar()
st.sidebar.markdown("### 📈 Health Tracker")
st.sidebar.info("Tracking your vitals regularly can help early detection of health issues.")

# Main content
st.markdown('<h1 class="page-header">❤️ Health Vitals</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Log and monitor your key health metrics</p>', unsafe_allow_html=True)
st.markdown("---")

# SECTION 1: LOG VITALS
st.markdown('<p class="section-title">📝 Log New Entry</p>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Move selectbox OUTSIDE the form to trigger updates
    vital_type = st.selectbox(
        "Select Metric Type",
        ["Blood Pressure", "Blood Sugar", "Heart Rate (Pulse)", "Weight", "Body Temperature", "SpO2"]
    )
    
    with st.form("log_vital_form", clear_on_submit=True):
        
        col1, col2 = st.columns(2)
        
        with col1: # Input fields
            # Dynamic input based on type
            if vital_type == "Blood Pressure":
                sys_bp = st.number_input("Systolic (Upper)", 60, 250, 120, key=f"sys_{vital_type}")
                dia_bp = st.number_input("Diastolic (Lower)", 40, 150, 80, key=f"dia_{vital_type}")
                value = f"{sys_bp}/{dia_bp}"
                unit = "mmHg"
            elif vital_type == "Blood Sugar":
                value = str(st.number_input("Level", 0, 600, 100, key=f"sugar_{vital_type}"))
                unit = st.selectbox("Unit", ["mg/dL", "mmol/L"], key=f"sugar_unit_{vital_type}")
            elif vital_type == "Weight":
                value = str(st.number_input("Weight(KG)", 0.0, 300.0, 70.0, step=0.1, key=f"weight_{vital_type}"))
                unit = "kg"
            elif vital_type == "Body Temperature":
                value = str(st.number_input("Temperature", 30.0, 45.0, 36.6, step=0.1, key=f"temp_{vital_type}"))
                unit = "°C"
            elif vital_type == "Heart Rate (Pulse)":
                value = str(st.number_input("Rate", 30, 220, 72, key=f"pulse_{vital_type}"))
                unit = "bpm"
            elif vital_type == "SpO2":
                value = str(st.number_input("Oxygen Level", 50, 100, 98, key=f"spo2_{vital_type}"))
                unit = "%"
                
        with col2: # Date/Time
            log_date = st.date_input("Date", date.today())
            log_time = st.time_input("Time", datetime.now().time())
            
        notes = st.text_area("Notes (Optional)", placeholder="e.g., Fasting, After run...")
        
        submitted = st.form_submit_button("💾 Save Log", use_container_width=True)
        
        if submitted:
            # Save to DB
            st.session_state.db.add_vital(
                log_date.isoformat(),
                log_time.strftime("%H:%M"),
                vital_type,
                value,
                unit,
                notes
            )
            st.success(f"✅ Logged {vital_type}: {value} {unit}")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# SECTION 2: CHARTS & HISTORY
st.markdown('<p class="section-title">📊 Trends & History</p>', unsafe_allow_html=True)

# Get data
vitals = st.session_state.db.get_all_vitals()

if not vitals:
    st.info("No vitals logged yet. Start tracking above!")
else:
    # Convert to DF
    df = pd.DataFrame(vitals)
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    
    # Filter by type for chart
    unique_types = df['vital_type'].unique()
    selected_type = st.selectbox("Select metric to view", unique_types)
    
    chart_data = df[df['vital_type'] == selected_type].copy()
    chart_data = chart_data.sort_values('datetime')
    
    # Specific handling for BP (split string to numeric)
    if selected_type == "Blood Pressure":
        # Split "120/80" -> 120, 80
        try:
            chart_data[['systolic', 'diastolic']] = chart_data['value'].str.split('/', expand=True).astype(int)
            chart_cols = ['systolic', 'diastolic']
        except:
             chart_cols = []
    else:
        # Just convert value to float
        chart_data['numeric_value'] = pd.to_numeric(chart_data['value'], errors='coerce')
        chart_cols = ['numeric_value']

    # Display key stats (latest)
    if not chart_data.empty:
        latest = chart_data.iloc[-1]
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"""
            <div class="vital-card">
                <div class="vital-label">Last Recorded</div>
                <div class="vital-value">{latest['value']}<span class="vital-unit">{latest['unit']}</span></div>
                <div class="vital-label">{latest['date']} {latest['time']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if chart_cols:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.line_chart(chart_data.set_index('datetime')[chart_cols], height=250)
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📜 Recent Logs")
    
    # Simple table
    display_df = df[df['vital_type'] == selected_type][['date', 'time', 'value', 'unit', 'notes', 'id']].sort_values(['date', 'time'], ascending=False)
    
    for idx, row in display_df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 4, 1])
        with col1:
            st.write(f"**{row['date']}**")
        with col2:
            st.write(f"{row['time']}")
        with col3:
             st.write(f"**{row['value']}** {row['unit']}")
             if row['notes']:
                 st.caption(f"📝 {row['notes']}")
        with col4:
            if st.button("🗑️", key=f"del_vital_{row['id']}", type="secondary"):
                st.session_state.db.delete_vital(row['id'])
                st.rerun()
        st.write("---")

render_footer(st)
