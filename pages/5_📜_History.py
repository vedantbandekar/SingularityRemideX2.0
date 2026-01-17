"""
Remidex - History & Daily Log Page
Track medication intake and view history
"""

import streamlit as st
import sys
import os
import csv
import io
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import Database
from utils.ai_helper import get_medicine_search
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="History & Log | Remidex",
    page_icon="📜",
    layout="wide"
)

# Authentication
from utils.auth import require_auth
require_auth()

# Inject premium CSS
inject_css(st)

# Additional page-specific CSS
st.markdown("""
<style>
    .today-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        transition: all 0.3s ease;
    }
    
    .today-card:hover {
        border-color: var(--primary-light);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
    }
    
    .today-card h4 {
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        font-size: 1.2rem;
    }
    
    .time-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: var(--text-primary);
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
    }
    
    .taken-indicator {
        color: var(--success);
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .history-entry {
        background: var(--glass-bg);
        border-left: 4px solid var(--primary);
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
        border-radius: 0 12px 12px 0;
        transition: all 0.3s ease;
    }
    
    .history-entry:hover {
        background: var(--bg-elevated);
        border-left-color: var(--accent);
    }
    
    .date-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 1.5rem 0 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .stats-card {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--text-primary);
    }
    
    .stats-label {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
        margin-top: 0.25rem;
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }
    
    .current-date {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
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
from utils.sidebar import render_ai_sidebar

render_ai_sidebar()

# Main content
st.markdown('<h1 class="page-header">📜 History & Daily Log</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Track your daily medication intake and view your history</p>', unsafe_allow_html=True)
st.markdown("---")

# Today's date display
today = date.today()
st.markdown(f'<p class="current-date">📅 Today: <strong>{today.strftime("%A, %B %d, %Y")}</strong></p>', unsafe_allow_html=True)

# SECTION 1: TODAY'S MEDICATIONS
st.markdown('<p class="section-title">✅ Today\'s Medications</p>', unsafe_allow_html=True)
st.markdown("*Check off medicines as you take them*")

# Get scheduled medicines with their alert times
medicines = st.session_state.db.get_all_medicines()
today_history = st.session_state.db.get_today_history()

# Create a set of taken medicine+time combinations
taken_today = set()
for h in today_history:
    taken_today.add(f"{h['medicine_name']}_{h['taken_time']}")

if not medicines:
    st.markdown("""
    <div class="info-box">
        📝 No medicines scheduled. Go to 'Add Medicine' to schedule your medications.
    </div>
    """, unsafe_allow_html=True)
else:
    # Group by medicine and show each alert time
    for med in medicines:
        st.markdown(f"""
        <div class="today-card">
            <h4>💊 {med['name']}</h4>
            <p style="color: var(--text-secondary); margin: 0.3rem 0;">
                {med['dosage']} — {med['frequency']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if med['alert_times']:
            for alert_time in med['alert_times']:
                key = f"{med['name']}_{alert_time}"
                is_taken = key in taken_today
                
                # Layout: Time (Left) ----- Spacer ----- Action (Right)
                col1, col2, col3 = st.columns([2, 6, 2])
                
                with col1:
                    st.markdown(f'<span class="time-badge">🔔 {alert_time}</span>', unsafe_allow_html=True)
                
                with col3:
                    if is_taken:
                        st.markdown('<div style="text-align: right;"><span class="taken-indicator">✅ Taken</span></div>', unsafe_allow_html=True)
                    else:
                        # Checkbox to mark as taken - aligned to right via column
                        if st.checkbox(
                            "Mark Taken",
                            key=f"check_{med['id']}_{alert_time}",
                            value=False,
                            label_visibility="visible"
                        ):
                            # Log to history
                            st.session_state.db.add_history(
                                med['name'],
                                today.isoformat(),
                                alert_time
                            )
                            
                            # Decrement supply
                            supply_decremented = st.session_state.db.decrement_supply(med['name'], 1)
                            
                            if supply_decremented:
                                st.success(f"Updated supply!")
                            st.rerun()
                
                st.markdown("---")
        else:
            st.markdown("*No specific alert times set*")
            
            # Allow logging without specific time
            col1, col2 = st.columns([8, 2])
            with col2:
                if st.button(f"Mark Taken", key=f"take_now_{med['id']}", use_container_width=True):
                    current_time = datetime.now().strftime("%H:%M")
                    st.session_state.db.add_history(
                        med['name'],
                        today.isoformat(),
                        current_time
                    )
                    st.session_state.db.decrement_supply(med['name'], 1)
                    st.success(f"Logged at {current_time}")
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")

# SECTION 2: MEDICATION HISTORY
st.markdown('<p class="section-title">📚 Medication History</p>', unsafe_allow_html=True)

# Stats summary
all_history = st.session_state.db.get_all_history()
today_count = len(today_history)

# Calculate weekly stats
week_ago = (today - timedelta(days=7)).isoformat()
weekly_count = len([h for h in all_history if h['taken_date'] >= week_ago])

stats_col1, stats_col2, stats_col3 = st.columns(3)
with stats_col1:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{today_count}</div>
        <div class="stats-label">📊 Today</div>
    </div>
    """, unsafe_allow_html=True)
with stats_col2:
    st.markdown(f"""
    <div class="stats-card" style="background: linear-gradient(135deg, var(--accent), #06B6D4);">
        <div class="stats-number">{weekly_count}</div>
        <div class="stats-label">📈 This Week</div>
    </div>
    """, unsafe_allow_html=True)
with stats_col3:
    st.markdown(f"""
    <div class="stats-card" style="background: linear-gradient(135deg, var(--success), #059669);">
        <div class="stats-number">{len(all_history)}</div>
        <div class="stats-label">📋 Total</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Filter & Download options
filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
with filter_col1:
    filter_option = st.selectbox(
        "Filter by",
        ["All History", "Today", "Last 7 Days", "Last 30 Days"]
    )

with filter_col2:
    # Prepare CSV data
    if all_history:
        output = io.StringIO()
        fieldnames = ['id', 'medicine_name', 'taken_date', 'taken_time']
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_history)
        csv_data = output.getvalue().encode('utf-8')
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"remidex_history_{date.today()}.csv",
            mime="text/csv",
        )

with filter_col3:
    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.db.clear_all_history()
        st.success("History cleared!")
        st.rerun()

# Filter history based on selection
if filter_option == "Today":
    filtered_history = today_history
elif filter_option == "Last 7 Days":
    week_ago = (today - timedelta(days=7)).isoformat()
    filtered_history = [h for h in all_history if h['taken_date'] >= week_ago]
elif filter_option == "Last 30 Days":
    month_ago = (today - timedelta(days=30)).isoformat()
    filtered_history = [h for h in all_history if h['taken_date'] >= month_ago]
else:
    filtered_history = all_history

st.markdown("---")

# Display history
if not filtered_history:
    st.markdown("""
    <div class="info-box">
        📝 No history entries found for the selected filter.
    </div>
    """, unsafe_allow_html=True)
else:
    # Group by date
    history_by_date = {}
    for entry in filtered_history:
        date_key = entry['taken_date']
        if date_key not in history_by_date:
            history_by_date[date_key] = []
        history_by_date[date_key].append(entry)
    
    # Sort dates descending
    for date_key in sorted(history_by_date.keys(), reverse=True):
        entries = history_by_date[date_key]
        
        # Parse and format date
        try:
            display_date = datetime.strptime(date_key, "%Y-%m-%d").strftime("%A, %B %d, %Y")
        except:
            display_date = date_key
        
        st.markdown(f'<p class="date-header">📅 {display_date}</p>', unsafe_allow_html=True)
        
        for entry in sorted(entries, key=lambda x: x['taken_time'], reverse=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**💊 {entry['medicine_name']}**")
            
            with col2:
                st.markdown(f"🕐 {entry['taken_time']}")
            
            with col3:
                if st.button("🗑️", key=f"del_hist_{entry['id']}", help="Delete entry"):
                    st.session_state.db.delete_history(entry['id'])
                    st.rerun()
            
            st.markdown("---")

# Footer tips
st.markdown("---")
st.markdown('<p class="section-title">💡 Tips for Better Medication Adherence</p>', unsafe_allow_html=True)
tips_col1, tips_col2, tips_col3 = st.columns(3)

with tips_col1:
    st.markdown("""
    <div class="tip-card">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⏰</div>
        <div style="color: var(--accent); font-weight: 600; margin-bottom: 0.5rem;">Set Reminders</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
            Use phone alarms alongside Remidex alerts for better adherence to your medication schedule.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tips_col2:
    st.markdown("""
    <div class="tip-card">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
        <div style="color: var(--accent); font-weight: 600; margin-bottom: 0.5rem;">Track Progress</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
            Regularly check your history to see your medication patterns and improve consistency.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tips_col3:
    st.markdown("""
    <div class="tip-card">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💊</div>
        <div style="color: var(--accent); font-weight: 600; margin-bottom: 0.5rem;">Don't Skip</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
            If you miss a dose, log it anyway and consult your doctor about what to do next.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
render_footer(st)
