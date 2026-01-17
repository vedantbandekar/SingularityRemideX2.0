"""
Remidex - Medicine Supply Page
Track medicine stock levels and get low supply warnings
"""

import streamlit as st
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import Database
from utils.ai_helper import get_medicine_search
from utils.styling import inject_css, render_sidebar_header, render_footer

# Page configuration
st.set_page_config(
    page_title="Medicine Supply | Remidex",
    page_icon="📦",
    layout="wide"
)

# Inject premium CSS
inject_css(st)

# Additional page-specific CSS
st.markdown("""
<style>
    .supply-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .supply-card:hover {
        border-color: var(--primary-light);
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15);
    }
    
    .supply-card-warning {
        border-color: var(--danger) !important;
        background: linear-gradient(145deg, rgba(239, 68, 68, 0.1), var(--glass-bg));
    }
    
    .supply-name {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.75rem;
    }
    
    .supply-stat {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin: 0.4rem 0;
    }
    
    .supply-stat strong {
        color: var(--text-primary);
    }
    
    .days-left {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .days-left-warning {
        background: linear-gradient(135deg, var(--danger), #F87171);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .progress-container {
        margin-top: 1rem;
    }
    
    .progress-bar {
        height: 8px;
        background: var(--bg-elevated);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    .warning-banner {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        color: #F87171;
        font-weight: 500;
        margin: 0.75rem 0;
        animation: pulse-warning 2s ease-in-out infinite;
    }
    
    @keyframes pulse-warning {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .ok-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        color: #34D399;
        font-weight: 500;
        margin: 0.75rem 0;
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
render_sidebar_header(st)

st.sidebar.markdown("### 🤖 AI Assistant")
st.sidebar.markdown("*Ask me about any medicine!*")

# Scrollable chat container
with st.sidebar.container(height=400):
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")
            st.markdown("---")

user_query = st.sidebar.chat_input("Ask about medicines...", key="supply_chat")
if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    response = st.session_state.medicine_search.answer_query(user_query)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()

# Main content
st.markdown('<h1 class="page-header">📦 Medicine Supply Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Track your medicine stock and get alerts before running out</p>', unsafe_allow_html=True)
st.markdown("---")

# Form and list columns
form_col, list_col = st.columns([1, 1])

with form_col:
    st.markdown('<p class="section-title">➕ Add/Update Supply</p>', unsafe_allow_html=True)
    
    with st.form("add_supply_form", clear_on_submit=True):
        # Get medicine names from scheduled medicines for suggestions
        scheduled_meds = st.session_state.db.get_all_medicines()
        med_names = [m['name'] for m in scheduled_meds]
        
        if med_names:
            medicine_name = st.selectbox(
                "Medicine Name",
                options=["-- Select or type new --"] + med_names,
                help="Select from scheduled medicines or enter a new name"
            )
            if medicine_name == "-- Select or type new --":
                medicine_name = st.text_input("Or enter new medicine name", key="new_med_name")
        else:
            medicine_name = st.text_input("Medicine Name", placeholder="Enter medicine name...")
        
        col1, col2 = st.columns(2)
        with col1:
            current_stock = st.number_input(
                "Current Stock (tablets/units)",
                min_value=0,
                max_value=10000,
                value=30,
                step=1,
                help="How many tablets/units do you currently have?"
            )
        
        with col2:
            daily_dosage = st.number_input(
                "Daily Dosage (units/day)",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                help="How many units do you take per day?"
            )
        
        alert_threshold = st.slider(
            "Alert me when supply is running low (days before)",
            min_value=1,
            max_value=30,
            value=5,
            help="Get notified this many days before your stock runs out"
        )
        
        # Calculate and show preview
        if daily_dosage > 0:
            days_supply = current_stock / daily_dosage
            end_date = date.today() + timedelta(days=days_supply)
            st.markdown(f"""
            <div class="info-box">
                📊 This supply will last approximately <strong>{days_supply:.0f} days</strong> (until {end_date.strftime('%B %d, %Y')})
            </div>
            """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("📦 Add/Update Supply", use_container_width=True)
        
        if submitted:
            if medicine_name and medicine_name != "-- Select or type new --":
                success = st.session_state.db.add_supply(
                    medicine_name,
                    current_stock,
                    daily_dosage,
                    alert_threshold
                )
                if success:
                    st.success(f"✅ Supply for **{medicine_name}** has been saved!")
                    st.rerun()
                else:
                    st.error("Failed to save supply. Please try again.")
            else:
                st.error("Please enter a medicine name.")

with list_col:
    st.markdown('<p class="section-title">📊 Your Supplies</p>', unsafe_allow_html=True)
    
    supplies = st.session_state.db.get_all_supplies()
    
    if not supplies:
        st.markdown("""
        <div class="info-box">
            📝 No supplies being tracked yet. Add your first supply to get started!
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary stats
        total_supplies = len(supplies)
        low_stock_count = 0
        
        for supply in supplies:
            med_name = supply['medicine_name']
            stock = supply['current_stock']
            daily = supply['daily_dosage']
            threshold = supply['alert_threshold']
            
            # Calculate days left
            days_left = stock / daily if daily > 0 else float('inf')
            end_date = date.today() + timedelta(days=days_left)
            
            # Check if low stock
            is_low = days_left <= threshold
            if is_low:
                low_stock_count += 1
            
            # Determine progress percentage (max 100 for display)
            progress_pct = min((days_left / 30) * 100, 100) if days_left < float('inf') else 100
            progress_color = "linear-gradient(90deg, #EF4444, #F87171)" if is_low else "linear-gradient(90deg, var(--primary), var(--accent))"
            
            # Card styling
            card_class = "supply-card supply-card-warning" if is_low else "supply-card"
            days_class = "days-left days-left-warning" if is_low else "days-left"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div class="supply-name">💊 {med_name}</div>
                <div class="supply-stat"><strong>Current Stock:</strong> {stock} units</div>
                <div class="supply-stat"><strong>Daily Dosage:</strong> {daily} units/day</div>
                <div class="supply-stat"><strong>Alert Threshold:</strong> {threshold} days</div>
                <div style="margin-top: 1rem;">
                    <span class="{days_class}">{days_left:.0f}</span>
                    <span style="color: var(--text-secondary);"> days remaining</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress_pct}%; background: {progress_color};"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Warning message
            if is_low:
                st.markdown(f"""
                <div class="warning-banner">
                    ⚠️ LOW STOCK ALERT! Only {days_left:.0f} days of supply remaining. 
                    Stock will run out by {end_date.strftime('%B %d, %Y')}!
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ok-banner">
                    ✅ Stock OK — Supply until {end_date.strftime('%B %d, %Y')}
                </div>
                """, unsafe_allow_html=True)
            
            # Actions
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                # Quick stock update
                new_stock = st.number_input(
                    "Update stock",
                    min_value=0,
                    value=stock,
                    key=f"stock_{supply['id']}"
                )
                if new_stock != stock:
                    if st.button("📝 Update", key=f"update_{supply['id']}"):
                        st.session_state.db.update_supply_stock(med_name, new_stock)
                        st.success("Stock updated!")
                        st.rerun()
            
            with action_col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete", key=f"del_{supply['id']}", type="secondary"):
                    st.session_state.db.delete_supply(supply['id'])
                    st.success(f"Deleted {med_name} from supply tracker")
                    st.rerun()
            
            st.markdown("---")
        
        # Summary at top
        if low_stock_count > 0:
            st.warning(f"⚠️ **{low_stock_count}** medicine(s) are running low on stock!")

# Tips section
st.markdown("---")
st.markdown('<p class="section-title">💡 Supply Management Tips</p>', unsafe_allow_html=True)
tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
    <div class="tip-card">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔄</div>
        <div style="color: var(--accent); font-weight: 600; margin-bottom: 0.5rem;">Regular Updates</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
            Update your stock count whenever you refill your medicines to keep accurate tracking.
        </div>
    </div>
    """, unsafe_allow_html=True)

with tips_col2:
    st.markdown("""
    <div class="tip-card">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📅</div>
        <div style="color: var(--accent); font-weight: 600; margin-bottom: 0.5rem;">Plan Ahead</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
            Set the alert threshold to give yourself enough time to refill prescriptions before running out.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
render_footer(st)
