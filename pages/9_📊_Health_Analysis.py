"""
Remidex - Health Analysis & Graph Page
Visualizes weekly health status, adherence, and vitals with color-coding.
"""

import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import Database
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Health Analysis | Remidex",
    page_icon="📊",
    layout="wide"
)

# Inject premium CSS
inject_css(st)

# Additional CSS for analysis page
st.markdown("""
<style>
    .status-card {
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    .status-healthy {
        background: rgba(50, 205, 50, 0.15);
        border-color: #32CD32;
    }
    .status-caution {
        background: rgba(255, 215, 0, 0.15);
        border-color: #FFD700;
    }
    .status-danger {
        background: rgba(255, 68, 68, 0.15);
        border-color: #FF4444;
    }
    .metric-val {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .metric-desc {
        font-size: 1.2rem;
        font-weight: 500;
        opacity: 0.8;
    }
    .chart-container {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
if 'db' not in st.session_state:
    st.session_state.db = Database()

# Sidebar
render_sidebar_header(st)

# Main content
st.markdown('<h1 class="page-header">📊 Health Analysis (Weekly)</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Visualizing your medicine adherence and vital trends</p>', unsafe_allow_html=True)
st.markdown("---")

# DATA GATHERING (Last 7 Days)
end_date = date.today()
start_date = end_date - timedelta(days=6)
dates_range = [ (start_date + timedelta(days=i)).isoformat() for i in range(7) ]

# 1. Fetch History & Calculate Adherence
history = st.session_state.db.get_all_history()
meds = st.session_state.db.get_all_medicines()

# Calculate total expected intakes per day
# This is a bit complex since alert times vary. For simplicity, we'll calculate:
# Expected = Count of active medication alerts * 7 days
total_alerts_per_day = sum([len(m['alert_times']) for m in meds])
total_expected = total_alerts_per_day * 7

# Count actual intakes in the range
intakes_in_range = [h for h in history if h['taken_date'] >= start_date.isoformat()]
total_taken = len(intakes_in_range)

adherence_pct = (total_taken / total_expected * 100) if total_expected > 0 else 0

# 2. Fetch Vitals
vitals_raw = st.session_state.db.get_all_vitals()
vitals_in_range = [v for v in vitals_raw if v['date'] >= start_date.isoformat()]

# CATEGORIZATION LOGIC
status = "Healthy"
color_class = "status-healthy"
status_msg = "You are doing great! Keep it up."
status_color = "#32CD32"

# Evaluate Vitals for danger zones
vitals_danger = False
vitals_caution = False

if vitals_in_range:
    for v in vitals_in_range:
        v_type = v['vital_type']
        v_val = v['value']
        
        if v_type == "Blood Pressure":
            try:
                sys, dia = map(int, v_val.split('/'))
                if sys >= 160 or dia >= 100: vitals_danger = True
                elif sys >= 140 or dia >= 90: vitals_caution = True
            except: pass
        elif v_type == "Blood Sugar":
            try:
                val = float(v_val)
                if val >= 200: vitals_danger = True
                elif val >= 140: vitals_caution = True
            except: pass
        elif v_type == "Heart Rate (Pulse)":
            try:
                val = int(v_val)
                if val >= 120 or val <= 40: vitals_danger = True
                elif val >= 100 or val <= 50: vitals_caution = True
            except: pass

# Final Combine
if adherence_pct < 50 or vitals_danger:
    status = "Unhealthy / Danger Zone"
    color_class = "status-danger"
    status_msg = "Warning: Several metrics are in the danger zone. Please consult a doctor."
    status_color = "#FF4444"
elif adherence_pct < 80 or vitals_caution:
    status = "Caution / Warning"
    color_class = "status-caution"
    status_msg = "Some metrics are slightly outside the normal range. Pay close attention."
    status_color = "#FFD700"

# SECTION 1: OVERALL STATUS
st.markdown(f"""
<div class="status-card {color_class}">
    <div class="metric-desc">Overall Health Status</div>
    <div class="metric-val">{status}</div>
    <div class="metric-desc">{status_msg}</div>
</div>
""", unsafe_allow_html=True)

col_sum1, col_sum2 = st.columns(2)
with col_sum1:
    st.markdown(f"""
    <div class="chart-container" style="text-align:center;">
        <div class="metric-val" style="color:{status_color}; font-size:2.5rem;">{int(adherence_pct)}%</div>
        <div class="metric-desc">Medicine Adherence</div>
    </div>
    """, unsafe_allow_html=True)
with col_sum2:
    v_count = len(vitals_in_range)
    st.markdown(f"""
    <div class="chart-container" style="text-align:center;">
        <div class="metric-val" style="color:var(--primary-light); font-size:2.5rem;">{v_count}</div>
        <div class="metric-desc">Vital Logs Recorded</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# SECTION 2: VISUALIZATIONS
st.markdown('<p class="section-title">📉 Detailed Trends</p>', unsafe_allow_html=True)

# 1. Adherence Bar Chart
adherence_counts = []
for d in dates_range:
    count = len([h for h in intakes_in_range if h['taken_date'] == d])
    adherence_counts.append(count)

fig_adh = px.area(
    x=dates_range, 
    y=adherence_counts,
    title="Daily Medicine Intake (Last 7 Days)",
    labels={'x': 'Date', 'y': 'Medicines Taken'},
    markers=True
)
fig_adh.update_traces(line_color=status_color, line_width=3)
fig_adh.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=400
)
st.plotly_chart(fig_adh, use_container_width=True)

# 2. Vitals Line Chart
if vitals_in_range:
    v_df = pd.DataFrame(vitals_in_range)
    # Filter for types that make sense for a line chart
    plot_types = ["Blood Pressure", "Blood Sugar", "Heart Rate (Pulse)", "Weight"]
    
    for pt in plot_types:
        pts_data = v_df[v_df['vital_type'] == pt].copy()
        if not pts_data.empty:
            st.markdown(f"#### {pt} Trend")
            
            # Special handling for BP
            if pt == "Blood Pressure":
                pts_data[['sys', 'dia']] = pts_data['value'].str.split('/', expand=True).astype(int)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=pts_data['date'], y=pts_data['sys'], name='Systolic', line=dict(color='#FF4444', width=3)))
                fig.add_trace(go.Scatter(x=pts_data['date'], y=pts_data['dia'], name='Diastolic', line=dict(color='#32CD32', width=3)))
                
                # Add zones
                fig.add_hrect(y0=140, y1=160, fillcolor="yellow", opacity=0.1, layer="below", line_width=0)
                fig.add_hrect(y0=160, y1=220, fillcolor="red", opacity=0.1, layer="below", line_width=0)
            else:
                pts_data['val_numeric'] = pd.to_numeric(pts_data['value'], errors='coerce')
                fig = px.line(pts_data, x='date', y='val_numeric', markers=True)
                fig.update_traces(line_color=status_color)
                
                # Add zones for Sugar
                if pt == "Blood Sugar":
                    fig.add_hrect(y0=140, y1=200, fillcolor="yellow", opacity=0.1, layer="below", line_width=0)
                    fig.add_hrect(y0=200, y1=400, fillcolor="red", opacity=0.1, layer="below", line_width=0)

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=350,
                xaxis_title="Date",
                yaxis_title="Value"
            )
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No vital logs available for the last 7 days to generate charts.")

render_footer(st)
