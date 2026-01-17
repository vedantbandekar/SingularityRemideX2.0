"""
Remidex - Health Analytics Page
Advanced visualization of health metrics with color-coded alerts
"""

import streamlit as st
import sys
import os
import pandas as pd
import altair as alt
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import Database
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Analytics | Remidex",
    page_icon="📊",
    layout="wide"
)

# Authentication
from utils.auth import require_auth
require_auth()

# Inject premium CSS
inject_css(st)

# Additional CSS
st.markdown("""
<style>
    .chart-box {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .chart-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .chart-subtitle {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
if 'db' not in st.session_state:
    st.session_state.db = Database()

# Sidebar
from utils.sidebar import render_ai_sidebar
render_ai_sidebar()

# Main Content
st.markdown('<h1 class="page-header">📊 Health Analytics</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Deep dive into your health trends</p>', unsafe_allow_html=True)
st.markdown("---")

# Main Container
st.markdown('<div class="chart-box">', unsafe_allow_html=True)
st.markdown('<div class="chart-title">📈 Unified Health Trends</div>', unsafe_allow_html=True)

# --- DATA PREPARATION ---
# We need a unified DataFrame: Index = Date, Columns = [BMI, Medicine Intake, Vital1, Vital2...]

# 1. Base Dates
# Get range from history or vitals
history = st.session_state.db.get_all_history()
vitals = st.session_state.db.get_all_vitals()
df_vitals = pd.DataFrame(vitals)
df_history = pd.DataFrame(history)

if df_vitals.empty and df_history.empty:
    st.info("No data available. Start tracking your health!")
else:
    # Prepare dictionaries to merge
    data_dict = {} # date_str -> {col: val}
    
    # helper
    def get_day_dict(d_date):
        d_str = d_date.strftime("%Y-%m-%d")
        if d_str not in data_dict: data_dict[d_str] = {}
        return data_dict[d_str]

    # A. Medicine Intake
    if not df_history.empty:
        df_history['date'] = pd.to_datetime(df_history['taken_date'])
        daily_counts = df_history.groupby('date').size()
        for d, count in daily_counts.items():
            get_day_dict(d)['Medicine Intake'] = count

    # B. BMI Calculation
    if not df_vitals.empty:
        df_vitals['datetime'] = pd.to_datetime(df_vitals['date'] + ' ' + df_vitals['time'])
        df_vitals['numeric_value'] = pd.to_numeric(df_vitals['value'], errors='coerce')
        
        # We need daily grouping for vitals to align
        # Weights
        w_df = df_vitals[df_vitals['vital_type'] == 'Weight'].copy()
        if not w_df.empty:
            w_daily = w_df.set_index('datetime').resample('D')['numeric_value'].mean()
            
            # Heights (Forward fill)
            h_df = df_vitals[df_vitals['vital_type'] == 'Height'].copy()
            h_val = 175 # Default fallback
            if not h_df.empty:
               h_val = h_df['numeric_value'].iloc[-1] 
            
            # Calculate BMI Day by Day
            for d, w in w_daily.items():
                if pd.notna(w):
                    bmi = w / ((h_val/100)**2)
                    get_day_dict(d)['BMI'] = bmi

        # C. Other Vitals (Systolic BP, Sugar)
        # Taking 'average' of the day for the graph
        target_vitals = {
            "Blood Sugar": "Abs Sugar", # Rename to avoid spacing issues?
            "Heart Rate (Pulse)": "Pulse"
        }
        
        for v_name, col_name in target_vitals.items():
             sub = df_vitals[df_vitals['vital_type'] == v_name]
             if not sub.empty:
                 daily_avg = sub.set_index('datetime').resample('D')['numeric_value'].mean()
                 for d, val in daily_avg.items():
                     if pd.notna(val):
                         get_day_dict(d)[col_name] = val
        
        # BP Special
        bp_df = df_vitals[df_vitals['vital_type'] == "Blood Pressure"]
        if not bp_df.empty:
             for _, row in bp_df.iterrows():
                 try:
                     sys_v, dia_v = map(int, row['value'].split('/'))
                     d = pd.to_datetime(row['date'])
                     # Just overwrite or avg? Simple approach: Last reading or avg
                     get_day_dict(d)['BP Systolic'] = sys_v
                 except: pass

    # Convert to DF
    if data_dict:
        chart_df = pd.DataFrame.from_dict(data_dict, orient='index')
        chart_df.index = pd.to_datetime(chart_df.index)
        chart_df.sort_index(inplace=True)
        
        if 'Medicine Intake' not in chart_df.columns:
            chart_df['Medicine Intake'] = 0.0
        if 'BMI' not in chart_df.columns:
            chart_df['BMI'] = None # NaN for gaps

        chart_df = chart_df.interpolate(method='time').fillna(0)

        # RENDER
        # Colors: Meds=Green, BMI=Yellow
        
        try:
            st.line_chart(
                data=chart_df[['Medicine Intake', 'BMI']],
                color=['#10B981', '#F59E0B'],
                use_container_width=True
            )
            st.caption("Tracking correlation between Medicine Intake and Body Mass Index (BMI).")
        except Exception as e:
            st.error(f"Could not render chart: {e}")

    else:
        st.warning("Data found but could not be processed into dates.")

st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION: RAW DATA LOGS ---
st.markdown("### 📋 Recent Body Metrics Logs", unsafe_allow_html=True)

if not df_vitals.empty:
    # Filter for Height and Weight
    body_df = df_vitals[df_vitals['vital_type'].isin(['Height', 'Weight'])].copy()
    if not body_df.empty:
        body_df = body_df.sort_values(['date', 'time'], ascending=False)
        
        # Format for display
        display_cols = ['date', 'time', 'vital_type', 'value', 'unit', 'notes']
        
        # Style the dataframe? Streamlit dataframe is interactive.
        st.dataframe(
            body_df[display_cols].style.applymap(
                lambda x: 'color: #F59E0B; font-weight: bold' if x == 'Weight' else ('color: #3B82F6; font-weight: bold' if x == 'Height' else ''),
                subset=['vital_type']
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No Height or Weight logs found.")
else:
    st.info("No vitals logged yet.")
render_footer(st)
