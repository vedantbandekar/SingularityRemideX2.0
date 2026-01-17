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

# Page configuration
st.set_page_config(
    page_title="Medicine Supply | Remidex",
    page_icon="📦",
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
    
    .supply-card {
        background: linear-gradient(145deg, var(--dark-gray), #0d0d0d);
        border: 2px solid var(--lime-green);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .supply-card-warning {
        border-color: #ff6b6b;
        background: linear-gradient(145deg, #1a1a1a, #2a1515);
    }
    
    .supply-name {
        color: var(--lime-green);
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .supply-stat {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin: 0.3rem 0;
    }
    
    .warning-banner {
        background: linear-gradient(135deg, #ff6b6b, #ee5a5a);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        font-weight: 500;
        animation: pulse-warning 2s ease-in-out infinite;
    }
    
    @keyframes pulse-warning {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }
    
    .ok-banner {
        background: linear-gradient(135deg, var(--lime-green), #28a428);
        color: var(--black);
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        font-weight: 500;
    }
    
    .days-left {
        font-size: 2rem;
        font-weight: 800;
        color: var(--lime-green);
    }
    
    .days-left-warning {
        color: #ff6b6b;
    }
    
    .stButton > button {
        background: linear-gradient(145deg, var(--lime-green), #28a428);
        color: var(--black) !important;
        font-weight: 600;
        border: none;
        border-radius: 10px;
    }
    
    .progress-bar {
        height: 10px;
        background: var(--dark-gray);
        border-radius: 5px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 0.3s ease;
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

user_query = st.sidebar.chat_input("Ask about medicines...", key="supply_chat")
if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    response = st.session_state.medicine_search.answer_query(user_query)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()

# Main content
st.markdown("# 📦 Medicine Supply Tracker")
st.markdown("*Track your medicine stock and get alerts before running out*")
st.markdown("---")

# Form and list columns
form_col, list_col = st.columns([1, 1])

with form_col:
    st.markdown("### ➕ Add/Update Supply")
    
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
            st.info(f"📊 This supply will last approximately **{days_supply:.0f} days** (until {end_date.strftime('%B %d, %Y')})")
        
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
    st.markdown("### 📊 Your Supplies")
    
    supplies = st.session_state.db.get_all_supplies()
    
    if not supplies:
        st.info("No supplies being tracked yet. Add your first supply!")
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
            progress_color = "#ff6b6b" if is_low else "#32CD32"
            
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
                    <span style="color: rgba(255,255,255,0.7);"> days remaining</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress_pct}%; background: {progress_color};"></div>
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
                    ✅ Stock OK - Supply until {end_date.strftime('%B %d, %Y')}
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
st.markdown("### 💡 Supply Management Tips")
tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.info("🔄 **Regular Updates** - Update your stock count whenever you refill your medicines to keep accurate tracking.")

with tips_col2:
    st.info("📅 **Plan Ahead** - Set the alert threshold to give yourself enough time to refill prescriptions.")
