import streamlit as st
from datetime import datetime, date
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))

from data_manager import DataManager
from pages import dashboard, tasks, finance, daily_log, analytics, vision_board, settings

st.set_page_config(
    page_title="Execution OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&family=Bebas+Neue&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #0a0a0f;
    color: #e8e8f0;
}
.stApp { background: #0a0a0f; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d0d1a;
    border-right: 1px solid #1e1e3a;
}
[data-testid="stSidebar"] .stRadio label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    padding: 0.5rem 0;
    color: #8888aa;
    cursor: pointer;
    transition: color 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #e8e8f0; }

/* Cards */
.card {
    background: #12121f;
    border: 1px solid #1e1e3a;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-accent {
    background: linear-gradient(135deg, #12121f 0%, #1a1a2e 100%);
    border: 1px solid #2d2d5e;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Headlines */
.page-title {
    font-family: 'Bebas Neue', cursive;
    font-size: 3rem;
    letter-spacing: 4px;
    color: #e8e8f0;
    margin: 0 0 0.25rem 0;
    line-height: 1;
}
.page-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #4a4a7a;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Progress bars */
.progress-wrap { margin: 0.75rem 0; }
.progress-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #8888aa;
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.4rem;
}
.progress-bar-bg {
    height: 10px;
    background: #1e1e3a;
    border-radius: 999px;
    overflow: hidden;
}
.progress-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s ease;
}

/* Metric boxes */
.metric-box {
    background: #12121f;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.metric-value {
    font-family: 'Bebas Neue', cursive;
    font-size: 2.2rem;
    letter-spacing: 2px;
    color: #7c6afc;
    line-height: 1.1;
}
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #4a4a7a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 0.2rem;
}

/* Accent colors */
.accent-purple { color: #7c6afc; }
.accent-green  { color: #3dffc0; }
.accent-orange { color: #ff8c42; }
.accent-red    { color: #ff4d6d; }
.accent-blue   { color: #4dc9ff; }

/* Buttons */
.stButton > button {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    background: #7c6afc;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.25rem;
    transition: background 0.2s, transform 0.15s;
}
.stButton > button:hover {
    background: #9b8dff;
    transform: translateY(-1px);
}

/* Inputs */
.stTextInput > div > input,
.stNumberInput > div > input,
.stTextArea > div > textarea,
.stSelectbox > div > div {
    background: #12121f !important;
    border: 1px solid #2d2d5e !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Dividers */
hr { border-color: #1e1e3a; }

/* Checkboxes */
.stCheckbox label { font-family: 'Space Grotesk', sans-serif; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2d2d5e; border-radius: 3px; }

/* Sidebar brand */
.sidebar-brand {
    font-family: 'Bebas Neue', cursive;
    font-size: 1.8rem;
    letter-spacing: 4px;
    color: #7c6afc;
    padding: 1rem 0 0.5rem 0;
    border-bottom: 1px solid #1e1e3a;
    margin-bottom: 1.5rem;
}
.sidebar-date {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #4a4a7a;
    letter-spacing: 1px;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Init data manager ────────────────────────────────────────────────────────
dm = DataManager()

# Show a one-time toast if local JSON data was just migrated to Supabase
_migrated = dm.get_migrated_keys()
if _migrated:
    st.toast(f"✅ Migrated local data to Supabase: {', '.join(_migrated)}", icon="☁️")

# ── Sidebar nav ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⚡ EXEC OS</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-date">{datetime.now().strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠  Dashboard", "✅  Daily Tasks", "💰  Finance", "📓  Daily Log", "📊  Analytics", "🎯  Vision Board", "⚙️  Settings"],
        label_visibility="collapsed"
    )

    cfg = dm.get_config()
    total_earned = dm.get_total_earned()
    goal = cfg["main_goal_amount"]
    pct = min(100, (total_earned / goal) * 100) if goal > 0 else 0

    st.markdown("---")
    storage_label = dm.storage_label()
    storage_color = "#3dffc0" if "Supabase" in storage_label else "#ff8c42"
    st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.62rem;color:{storage_color};letter-spacing:1px;margin-bottom:0.75rem">● {storage_label}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#4a4a7a;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.4rem'>
        Main Goal Progress
    </div>
    <div style='font-family:Bebas Neue,cursive;font-size:1.4rem;color:#7c6afc;letter-spacing:2px'>
        {pct:.1f}%
    </div>
    <div class='progress-bar-bg' style='margin-top:0.3rem'>
        <div class='progress-bar-fill' style='width:{pct}%;background:linear-gradient(90deg,#7c6afc,#3dffc0)'></div>
    </div>
    <div style='font-family:JetBrains Mono,monospace;font-size:0.6rem;color:#4a4a7a;margin-top:0.3rem'>
        KES {total_earned:,.0f} / {goal:,.0f}
    </div>
    """, unsafe_allow_html=True)

# ── Route pages ──────────────────────────────────────────────────────────────
p = page.split("  ", 1)[1]

if p == "Dashboard":
    dashboard.render(dm)
elif p == "Daily Tasks":
    tasks.render(dm)
elif p == "Finance":
    finance.render(dm)
elif p == "Daily Log":
    daily_log.render(dm)
elif p == "Analytics":
    analytics.render(dm)
elif p == "Vision Board":
    vision_board.render(dm)
elif p == "Settings":
    settings.render(dm)
