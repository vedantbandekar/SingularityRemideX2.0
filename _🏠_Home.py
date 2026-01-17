"""
Remidex - Smart Medication & Health Manager
Main Dashboard (Home Page)
"""

import streamlit as st
import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from utils.database import Database
from utils.ai_helper import get_medicine_search
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Home | Remidex",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject premium CSS
inject_css(st)

# Dashboard-specific CSS
st.markdown("""
<style>
    .hero-card {
        background: linear-gradient(135deg, rgba(50, 205, 50, 0.1), rgba(0, 0, 0, 0.3));
        border: 1px solid var(--primary-dark);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .metric-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .metric-card:hover {
        border-color: var(--primary-light);
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(50, 205, 50, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .dashboard-card {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.25rem;
        height: 100%;
        border: 1px solid var(--glass-border);
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .list-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .list-item:last-child {
        border-bottom: none;
    }
    
    .status-badge {
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-ok { background: rgba(50, 205, 50, 0.2); color: #32CD32; }
    .status-warning { background: rgba(255, 215, 0, 0.2); color: #FFD700; }
    .status-danger { background: rgba(255, 68, 68, 0.2); color: #FF4444; }
    
    .nav-btn {
        display: block;
        width: 100%;
        padding: 1rem;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        color: var(--text-primary);
        text-align: center;
        text-decoration: none;
        transition: all 0.2s;
        margin-bottom: 0.5rem;
    }
    
    .nav-btn:hover {
        border-color: var(--primary);
        background: rgba(50, 205, 50, 0.05);
    }

</style>
""", unsafe_allow_html=True)

# Initialize
if 'db' not in st.session_state:
    st.session_state.db = Database()
    # Ensure tables
    st.session_state.db._init_db()
if 'medicine_search' not in st.session_state:
    st.session_state.medicine_search = get_medicine_search()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
<<<<<<< HEAD
from utils.sidebar import render_ai_sidebar

render_ai_sidebar()
=======
render_sidebar_header(st)
st.sidebar.markdown("### 🏠 Dashboard")
st.sidebar.info("Welcome back! Here is your daily health overview.")

# Scrollable chat
with st.sidebar.container(height=300):
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
>>>>>>> 8acf574b2a3a38fa0451a4cf60d4aaff499c83d5

# --- MAIN CONTENT ---

# Hero Header
current_hour = datetime.now().hour
if 5 <= current_hour < 12:
    greeting = "Good Morning ☀️"
elif 12 <= current_hour < 18:
    greeting = "Good Afternoon 🌤️"
else:
    greeting = "Good Evening 🌙"

st.markdown(f'<h1 class="page-header">{greeting}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="page-subtitle">Today is <strong>{date.today().strftime("%A, %B %d, %Y")}</strong></p>', unsafe_allow_html=True)

# 1. TOP METRICS
streak = st.session_state.db.get_streak_days()
meds_count = len(st.session_state.db.get_all_medicines())
vitals_count = len(st.session_state.db.get_all_vitals())

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{streak} Days</div>
        <div class="metric-label">🔥 Current Streak</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{meds_count}</div>
        <div class="metric-label">💊 Active Medicines</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{vitals_count}</div>
        <div class="metric-label">❤️ Vitals Logged</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 2. INSIGHTS ROW (Appointments & Supply)
row2_col1, row2_col2 = st.columns(2)

# Appointments Widget
with row2_col1:

    st.markdown('<div class="card-title">🗓️ Next Appointment</div>', unsafe_allow_html=True)
    
    appts = st.session_state.db.get_all_appointments()
    today_iso = date.today().isoformat()
    # Filter upcoming
    upcoming = [a for a in appts if a['appt_date'] >= today_iso]
    
    if not upcoming:
        st.info("No upcoming appointments.")
        st.markdown("[Schedule one now ->](Appointments)")
    else:
        # Get nearest
        next_appt = upcoming[0] # Already sorted by date in DB query
        d_obj = datetime.strptime(next_appt['appt_date'], "%Y-%m-%d")
        days_left = (d_obj.date() - date.today()).days
        
        if days_left == 0:
            status = '<span class="status-badge status-warning">TODAY</span>'
        elif days_left == 1:
            status = '<span class="status-badge status-ok">TOMORROW</span>'
        else:
            status = f'<span class="status-badge status-ok">IN {days_left} DAYS</span>'
            
        st.markdown(f"""
        <div style="background:var(--bg-elevated); padding:1rem; border-radius:12px; margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span style="font-weight:bold; font-size:1.1rem; color:var(--primary-light);">
                    {next_appt['doctor_name']}
                </span>
                {status}
            </div>
            <div style="color:var(--text-secondary); font-size:0.9rem;">
                {next_appt['specialty']}
            </div>
            <div style="margin-top:0.5rem; font-weight:600;">
                 📅 {d_obj.strftime("%b %d")} at {next_appt['appt_time']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if len(upcoming) > 1:
            st.caption(f"And {len(upcoming)-1} more upcoming.")
            



# Supply Alert Widget
with row2_col2:

    st.markdown('<div class="card-title">📦 Supply Alerts</div>', unsafe_allow_html=True)
    
    supplies = st.session_state.db.get_all_supplies()
    low_stock = []
    
    for s in supplies:
        daily = s['daily_dosage']
        days = s['current_stock'] / daily if daily > 0 else 999
        if days <= s['alert_threshold']:
            low_stock.append(s)
            
    if not low_stock:
        st.success("✅ All supplies are fully stocked!")
    else:
        for s in low_stock[:3]: # Show max 3
            days = int(s['current_stock'] / s['daily_dosage'])
            st.markdown(f"""
            <div class="list-item">
                <div>
                    <strong>{s['medicine_name']}</strong><br>
                    <span style="font-size:0.8rem; color:var(--text-secondary);">Only {s['current_stock']} left</span>
                </div>
                <span class="status-badge status-danger">{days} Days Left</span>
            </div>
            """, unsafe_allow_html=True)
            
        if len(low_stock) > 3:
            st.caption(f"...and {len(low_stock)-3} more.")
            


st.markdown("<br>", unsafe_allow_html=True)

# 3. RECENT VITALS

st.markdown('<div class="card-title">❤️ Recent Vitals</div>', unsafe_allow_html=True)

vitals = st.session_state.db.get_all_vitals()
if not vitals:
    st.info("No vitals logged recently.")
else:
    # Group by type and get latest
    latest_vitals = {}
    for v in vitals: # Ordered by date desc
        if v['vital_type'] not in latest_vitals:
            latest_vitals[v['vital_type']] = v
            
    # Display in columns (max 4)
    v_cols = st.columns(4)
    count = 0
    for v_type, data in latest_vitals.items():
        if count >= 4: break
        with v_cols[count]:
            st.markdown(f"""
            <div style="text-align:center; padding:0.5rem;">
                <div style="font-size:0.8rem; color:var(--text-secondary);">{v_type}</div>
                <div style="font-size:1.2rem; font-weight:bold; color:var(--primary-light);">{data['value']} <span style="font-size:0.8rem;">{data['unit']}</span></div>
                <div style="font-size:0.75rem; opacity:0.7;">{data['date']}</div>
            </div>
            """, unsafe_allow_html=True)
        count += 1



# Footer
st.markdown("---")
render_footer(st)
