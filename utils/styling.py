"""
Shared styling module for Remidex
Premium Glassmorphism theme with Indigo & Cyan palette
"""

def get_premium_css():
    """Return the premium CSS styling for all pages"""
    return """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Color Palette & Variables */
    :root {
        --primary: #32CD32;       /* Lime Green */
        --primary-light: #4cda4c; /* Lighter Lime */
        --primary-dark: #228B22;  /* Forest Green */
        --accent: #32CD32;        /* Lime Green (Accent) */
        --accent-dark: #228B22;
        --success: #32CD32;
        --warning: #FFD700;       /* Gold */
        --danger: #FF4444;        /* Red */
        --bg-dark: #000000;       /* Pure Black */
        --bg-card: #111111;       /* Very Dark Gray */
        --bg-elevated: #1a1a1a;   /* Dark Gray */
        --text-primary: #FFFFFF;  /* White */
        --text-secondary: #e0e0e0; /* Off-White */
        --glass-bg: rgba(20, 20, 20, 0.85); /* Black Glass */
        --glass-border: rgba(50, 205, 50, 0.3); /* Lime border hint */
    }
    
    /* Global Styles */
    .stApp {
        background-color: var(--bg-dark);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 15, 26, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        border-right: 1px solid var(--glass-border);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
    }
    
    /* Page Header */
    .page-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--text-primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .page-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
    }
    
    /* Navigation/Action Cards */
    .nav-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .nav-card:hover {
        border-color: var(--primary-light);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    
    .nav-card-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }
    
    .nav-card-title {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .nav-card-desc {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    /* Feature Badge */
    .feature-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.3rem;
        box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary/Delete Button */
    button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid var(--danger) !important;
        color: var(--danger) !important;
    }
    
    button[kind="secondary"]:hover {
        background: var(--danger) !important;
        color: white !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid var(--glass-border) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Metric Cards */
    .stat-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        border-color: var(--accent);
        transform: translateY(-3px);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }
    
    /* Sidebar Brand */
    .sidebar-brand {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-light), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.25rem;
    }
    
    .sidebar-tagline {
        color: var(--text-secondary);
        font-size: 0.85rem;
        opacity: 0.8;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: var(--text-secondary);
        font-size: 0.85rem;
        border-top: 1px solid var(--glass-border);
        margin-top: 3rem;
    }
    
    .footer strong {
        color: var(--primary-light);
    }
    
    /* Chat Styling */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: rgba(99, 102, 241, 0.1) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
    }
    
    /* Info/Warning/Error Boxes */
    .info-box {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        padding: 1rem;
        color: var(--text-primary);
    }
    
    /* Medicine Card (List) */
    .medicine-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .medicine-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary-light);
        margin-bottom: 0.25rem;
    }
    
    .medicine-info {
        font-size: 0.9rem;
        color: var(--text-secondary);
    }
</style>
"""


def inject_css(st):
    """Inject the premium CSS into a Streamlit app"""
    st.markdown(get_premium_css(), unsafe_allow_html=True)


def render_sidebar_header(st):
    """Render the standard sidebar header"""
    st.sidebar.markdown('<p class="sidebar-brand">💊 Remidex</p>', unsafe_allow_html=True)
    st.sidebar.markdown('<p class="sidebar-tagline">Smart Medication Manager</p>', unsafe_allow_html=True)
    st.sidebar.markdown("---")


def render_footer(st):
    """Render the standard footer"""
    st.markdown("""
    <div class="footer">
        Made with ❤️ for better health management | <strong>Remidex</strong> © 2026
    </div>
    """, unsafe_allow_html=True)
