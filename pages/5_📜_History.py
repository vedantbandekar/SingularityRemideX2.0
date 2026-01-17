"""
Remidex - History & Daily Log Page
Track medication intake and view history
"""

import streamlit as st
import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import Database
from utils.ai_helper import get_medicine_search

# Page configuration
st.set_page_config(
    page_title="History & Log | Remidex",
    page_icon="📜",
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
    
    .today-card {
        background: linear-gradient(145deg, var(--dark-gray), #0d0d0d);
        border: 2px solid var(--lime-green);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    
    .medicine-item {
        background: var(--dark-gray);
        border: 1px solid rgba(50, 205, 50, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .medicine-item-taken {
        border-color: var(--lime-green);
        background: rgba(50, 205, 50, 0.1);
    }
    
    .time-badge {
        background: var(--lime-green);
        color: var(--black);
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .history-entry {
        background: var(--dark-gray);
        border-left: 4px solid var(--lime-green);
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
    }
    
    .history-date {
        color: var(--lime-green);
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .history-medicine {
        color: var(--white);
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .history-time {
        color: rgba(255,255,255,0.6);
        font-size: 0.85rem;
    }
    
    .stats-card {
        background: linear-gradient(145deg, var(--lime-green), #28a428);
        color: var(--black);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 800;
    }
    
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.8;
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
    }
    
    .checkbox-container {
        background: var(--dark-gray);
        border: 1px solid rgba(50, 205, 50, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .taken-indicator {
        color: var(--lime-green);
        font-weight: 600;
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
st.sidebar.markdown("# 💊 Remidex")
st.sidebar.markdown("*Your Smart Medication Manager*")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🤖 AI Assistant")
for msg in st.session_state.chat_history[-3:]:
    if msg["role"] == "user":
        st.sidebar.markdown(f"**You:** {msg['content'][:40]}...")
    else:
        st.sidebar.markdown(f"**AI:** {msg['content'][:80]}...")

user_query = st.sidebar.chat_input("Ask about medicines...", key="history_chat")
if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    response = st.session_state.medicine_search.answer_query(user_query)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()

# Main content
st.markdown("# 📜 History & Daily Log")
st.markdown("*Track your daily medication intake and view your history*")
st.markdown("---")

# Today's date display
today = date.today()
st.markdown(f"### 📅 Today: {today.strftime('%A, %B %d, %Y')}")

# Two columns: Today's meds and History
today_col, history_col = st.columns([1, 1])

with today_col:
    st.markdown("### ✅ Today's Medications")
    st.markdown("*Check off medicines as you take them*")
    
    # Get scheduled medicines with their alert times
    medicines = st.session_state.db.get_all_medicines()
    today_history = st.session_state.db.get_today_history()
    
    # Create a set of taken medicine+time combinations
    taken_today = set()
    for h in today_history:
        taken_today.add(f"{h['medicine_name']}_{h['taken_time']}")
    
    if not medicines:
        st.info("No medicines scheduled. Go to 'Add Medicine' to schedule your medications.")
    else:
        # Group by medicine and show each alert time
        for med in medicines:
            st.markdown(f"""
            <div class="today-card">
                <h4 style="margin: 0;">💊 {med['name']}</h4>
                <p style="color: rgba(255,255,255,0.7); margin: 0.3rem 0;">
                    {med['dosage']} - {med['frequency']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if med['alert_times']:
                for alert_time in med['alert_times']:
                    key = f"{med['name']}_{alert_time}"
                    is_taken = key in taken_today
                    
                    col1, col2, col3 = st.columns([1, 3, 2])
                    
                    with col1:
                        st.markdown(f'<span class="time-badge">🔔 {alert_time}</span>', unsafe_allow_html=True)
                    
                    with col2:
                        if is_taken:
                            st.markdown('<span class="taken-indicator">✅ Taken</span>', unsafe_allow_html=True)
                        else:
                            # Checkbox to mark as taken
                            if st.checkbox(
                                f"Mark as taken",
                                key=f"check_{med['id']}_{alert_time}",
                                value=False
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
                                    st.success(f"✅ Logged {med['name']} and updated supply!")
                                else:
                                    st.success(f"✅ Logged {med['name']}!")
                                    st.info("💡 Tip: Add this medicine to Supply Tracker to monitor stock.")
                                
                                st.rerun()
                    
                    with col3:
                        # Quick log with custom time
                        pass
                    
                    st.markdown("---")
            else:
                st.markdown("*No specific alert times set*")
                
                # Allow logging without specific time
                if st.button(f"Mark as taken now", key=f"take_now_{med['id']}"):
                    current_time = datetime.now().strftime("%H:%M")
                    st.session_state.db.add_history(
                        med['name'],
                        today.isoformat(),
                        current_time
                    )
                    st.session_state.db.decrement_supply(med['name'], 1)
                    st.success(f"✅ Logged {med['name']} at {current_time}")
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick add manual entry
    st.markdown("---")
    st.markdown("#### ➕ Quick Log (Manual Entry)")
    
    with st.form("quick_log_form", clear_on_submit=True):
        ql_col1, ql_col2 = st.columns(2)
        with ql_col1:
            quick_med_name = st.text_input("Medicine Name", placeholder="Enter medicine name")
        with ql_col2:
            quick_time = st.time_input("Time Taken", value=datetime.now().time())
        
        if st.form_submit_button("📝 Log Entry", use_container_width=True):
            if quick_med_name:
                st.session_state.db.add_history(
                    quick_med_name,
                    today.isoformat(),
                    quick_time.strftime("%H:%M")
                )
                st.session_state.db.decrement_supply(quick_med_name, 1)
                st.success(f"✅ Logged {quick_med_name}")
                st.rerun()
            else:
                st.error("Please enter a medicine name.")

with history_col:
    st.markdown("### 📚 Medication History")
    
    # Stats summary
    all_history = st.session_state.db.get_all_history()
    today_count = len(today_history)
    
    # Calculate weekly stats
    week_ago = (today - timedelta(days=7)).isoformat()
    weekly_count = len([h for h in all_history if h['taken_date'] >= week_ago])
    
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    with stats_col1:
        st.metric("📊 Today", today_count)
    with stats_col2:
        st.metric("📈 This Week", weekly_count)
    with stats_col3:
        st.metric("📋 Total", len(all_history))
    
    st.markdown("---")
    
    # Filter options
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_option = st.selectbox(
            "Filter by",
            ["All History", "Today", "Last 7 Days", "Last 30 Days"]
        )
    with filter_col2:
        if st.button("🗑️ Clear All History", type="secondary"):
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
        st.info("No history entries found for the selected filter.")
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
            
            st.markdown(f"#### 📅 {display_date}")
            
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
st.markdown("### 💡 Tips for Better Medication Adherence")
tips_col1, tips_col2, tips_col3 = st.columns(3)

with tips_col1:
    st.info("⏰ **Set Reminders** - Use phone alarms alongside Remidex alerts for better adherence.")

with tips_col2:
    st.info("📊 **Track Progress** - Regularly check your history to see your medication patterns.")

with tips_col3:
    st.info("💊 **Don't Skip** - If you miss a dose, log it anyway and consult your doctor about what to do.")
