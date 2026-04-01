import streamlit as st
from datetime import date

SOURCES = ["Freelance", "Content Creation", "Trading", "Client Work", "Consulting", "Product Sales", "Other"]

def render(dm):
    cfg = dm.get_config()
    total = dm.get_total_earned()
    goal = cfg["main_goal_amount"]
    pct = min(100, (total / goal) * 100) if goal > 0 else 0

    st.markdown('<p class="page-title">FINANCE</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">// Every shilling logged. Every shilling counted.</p>', unsafe_allow_html=True)

    # ── Summary strip ─────────────────────────────────────────────────────────
    entries = dm.get_income_entries()
    today_total = sum(e["amount"] for e in entries if e.get("date") == date.today().isoformat())
    this_month = date.today().strftime("%Y-%m")
    month_total = sum(e["amount"] for e in entries if e.get("date", "").startswith(this_month))

    c1, c2, c3, c4 = st.columns(4)
    def mbox(val, label, color="#7c6afc"):
        return f'<div class="metric-box"><div class="metric-value" style="font-size:1.4rem;color:{color}">{val}</div><div class="metric-label">{label}</div></div>'

    with c1: st.markdown(mbox(f"KES {total:,.0f}", "TOTAL EARNED", "#3dffc0"), unsafe_allow_html=True)
    with c2: st.markdown(mbox(f"KES {today_total:,.0f}", "EARNED TODAY", "#ff8c42"), unsafe_allow_html=True)
    with c3: st.markdown(mbox(f"KES {month_total:,.0f}", "THIS MONTH", "#4dc9ff"), unsafe_allow_html=True)
    with c4: st.markdown(mbox(f"{pct:.1f}%", "GOAL PROGRESS", "#7c6afc"), unsafe_allow_html=True)

    # Main goal bar
    st.markdown(f"""
    <div class="card" style="margin-top:1rem">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;text-transform:uppercase;letter-spacing:2px;margin-bottom:0.75rem">
            {cfg['main_goal_label']} — KES {goal:,.0f}
        </div>
        <div style="height:12px;background:#1e1e3a;border-radius:999px;overflow:hidden">
            <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#7c6afc,#3dffc0);border-radius:999px"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;margin-top:0.4rem">
            <span>KES {total:,.0f} earned</span>
            <span>KES {goal - total:,.0f} remaining</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Log income ────────────────────────────────────────────────────────────
    st.markdown("### ➕ Log Income")
    with st.form("income_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Amount (KES)", min_value=1.0, step=100.0, format="%.2f")
        with col2:
            source = st.selectbox("Source", SOURCES)
        note = st.text_input("Note (optional)", placeholder="e.g. Video editing for client X")
        submitted = st.form_submit_button("💰 Log Income")
        if submitted and amount > 0:
            dm.add_income(amount, source, note)
            st.success(f"✅ KES {amount:,.2f} from {source} logged!")
            st.rerun()

    # ── Sub-goals progress ────────────────────────────────────────────────────
    st.markdown("### 🎯 Sub-Goal Allocation")
    sub_progress = dm.get_sub_goal_progress()
    colors = ["#7c6afc", "#3dffc0", "#ff8c42", "#4dc9ff", "#ff4d6d"]
    for i, (sg, saved) in enumerate(sub_progress):
        p2 = min(100, (saved / sg["amount"]) * 100) if sg["amount"] > 0 else 0
        c = colors[i % len(colors)]
        status = "✅ FUNDED" if p2 >= 100 else f"{p2:.1f}%"
        st.markdown(f"""
        <div class="card" style="border-left:3px solid {c}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem">
                <div>
                    <span style="font-size:1.3rem">{sg.get('icon','🎯')}</span>
                    <span style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.9rem;color:#e8e8f0;margin-left:0.5rem">{sg['label']}</span>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:{c}">{status}</div>
            </div>
            <div style="height:8px;background:#1e1e3a;border-radius:999px;overflow:hidden">
                <div style="height:100%;width:{p2}%;background:{c};border-radius:999px"></div>
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;margin-top:0.3rem">
                KES {saved:,.0f} / {sg['amount']:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Income history ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 Income History")

    if not entries:
        st.markdown('<div class="card" style="color:#4a4a7a;text-align:center;font-family:JetBrains Mono,monospace">No income logged yet. Start earning.</div>', unsafe_allow_html=True)
    else:
        for i, e in enumerate(reversed(entries)):
            idx = len(entries) - 1 - i
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 3, 3, 2, 1])
                with col1:
                    st.markdown(f'<span style="font-family:JetBrains Mono,monospace;font-size:0.75rem;color:#4a4a7a">{e["date"]}</span>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<span style="font-family:Space Grotesk,sans-serif;font-weight:600;color:#3dffc0">KES {e["amount"]:,.2f}</span>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.85rem;color:#8888aa">{e["source"]}</span>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<span style="font-family:Space Grotesk,sans-serif;font-size:0.8rem;color:#4a4a7a">{e.get("note","")[:30]}</span>', unsafe_allow_html=True)
                with col5:
                    if st.button("🗑", key=f"del_{idx}"):
                        dm.delete_income(idx)
                        st.rerun()
