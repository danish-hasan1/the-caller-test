import streamlit as st

st.set_page_config(
    page_title="The Caller",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Dark industrial theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Root variables */
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #111118;
    --bg-card: #16161f;
    --bg-hover: #1e1e2e;
    --accent: #e8c547;
    --accent-dim: #c9a82c;
    --accent-glow: rgba(232, 197, 71, 0.15);
    --text-primary: #f0f0f8;
    --text-secondary: #8888aa;
    --text-muted: #55556a;
    --border: #2a2a3a;
    --border-accent: rgba(232, 197, 71, 0.4);
    --success: #4ecb71;
    --warning: #f59e0b;
    --danger: #ef4444;
    --info: #60a5fa;
    --radius: 6px;
}

/* Global */
html, body, .stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}

.stApp { background: var(--bg-primary) !important; }

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Sidebar */
.css-1d391kg, [data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stMarkdown { color: var(--text-secondary); }

/* Sidebar nav items */
[data-testid="stSidebarNav"] a {
    color: var(--text-secondary) !important;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    border-radius: var(--radius);
    transition: all 0.2s;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    color: var(--accent) !important;
    background: var(--accent-glow) !important;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #0a0a0f !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    letter-spacing: 0.05em;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 8px 18px !important;
    cursor: pointer;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--accent-dim) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px var(--accent-glow) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-glow) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent-glow) !important;
}

/* Labels */
.stTextInput label, .stTextArea label, .stSelectbox label,
.stNumberInput label, .stMultiSelect label {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-family: 'Space Mono', monospace !important;
    letter-spacing: 0.05em;
}

/* Metrics */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 16px !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 11px !important;
    font-family: 'Space Mono', monospace !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 28px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.08em;
    border-bottom: 2px solid transparent !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.streamlit-expanderContent {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Alerts */
.stAlert {
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
}

/* Select box dropdown */
[data-baseweb="popover"] { background: var(--bg-card) !important; }
[data-baseweb="option"] { background: var(--bg-card) !important; color: var(--text-primary) !important; }
[data-baseweb="option"]:hover { background: var(--bg-hover) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Custom card component */
.caller-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.caller-card:hover { border-color: var(--border-accent); }

.status-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.status-new { background: rgba(96,165,250,0.15); color: #60a5fa; border: 1px solid rgba(96,165,250,0.3); }
.status-contacted { background: rgba(232,197,71,0.15); color: #e8c547; border: 1px solid rgba(232,197,71,0.3); }
.status-responded { background: rgba(168,85,247,0.15); color: #a855f7; border: 1px solid rgba(168,85,247,0.3); }
.status-screened { background: rgba(251,146,60,0.15); color: #fb923c; border: 1px solid rgba(251,146,60,0.3); }
.status-negotiating { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.status-closed { background: rgba(78,203,113,0.15); color: #4ecb71; border: 1px solid rgba(78,203,113,0.3); }
.status-rejected { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

.page-header {
    font-family: 'Space Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.page-sub {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 28px;
}
.mono-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.accent-text { color: var(--accent); }
</style>
""", unsafe_allow_html=True)

# Sidebar branding
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 28px 0;">
        <div style="font-family: 'Space Mono', monospace; font-size: 18px; font-weight: 700; color: #f0f0f8; letter-spacing: -0.02em;">
            📞 THE CALLER
        </div>
        <div style="font-size: 11px; color: #55556a; letter-spacing: 0.08em; margin-top: 4px; text-transform: uppercase;">
            AI Recruitment Agent
        </div>
        <div style="height: 1px; background: #2a2a3a; margin-top: 20px;"></div>
    </div>
    """, unsafe_allow_html=True)

# Main landing / redirect
st.markdown("""
<div style="display:flex; align-items:center; justify-content:center; min-height:70vh; flex-direction:column; text-align:center;">
    <div style="font-family:'Space Mono',monospace; font-size:48px; font-weight:700; color:#f0f0f8; letter-spacing:-0.03em; line-height:1.1;">
        THE<br><span style="color:#e8c547;">CALLER</span>
    </div>
    <div style="font-size:14px; color:#55556a; margin-top:16px; max-width:420px; line-height:1.7;">
        AI-powered recruitment agent. Sources leads, reaches out, screens, negotiates and closes — automatically.
    </div>
    <div style="margin-top:36px; display:flex; gap:12px; flex-wrap:wrap; justify-content:center;">
        <div style="background:#16161f; border:1px solid #2a2a3a; border-radius:6px; padding:12px 20px; font-family:'Space Mono',monospace; font-size:11px; color:#8888aa;">SOURCER →</div>
        <div style="background:rgba(232,197,71,0.1); border:1px solid rgba(232,197,71,0.4); border-radius:6px; padding:12px 20px; font-family:'Space Mono',monospace; font-size:11px; color:#e8c547;">THE CALLER ●</div>
        <div style="background:#16161f; border:1px solid #2a2a3a; border-radius:6px; padding:12px 20px; font-family:'Space Mono',monospace; font-size:11px; color:#8888aa;">→ VALIDATOR</div>
    </div>
    <div style="margin-top:36px; font-size:13px; color:#55556a;">
        ← Navigate using the sidebar
    </div>
</div>
""", unsafe_allow_html=True)
