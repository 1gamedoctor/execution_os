import streamlit as st
from datetime import date, datetime

def render(dm):
    cfg = dm.get_config()
    today = dm.get_day()
    total_earned = dm.get_total_earned()
    goal = cfg["main_goal_amount"]
    pct = min(100, (total_earned / goal) * 100) if goal > 0 else 0

    # ── Deadline countdown ───────────────────────────────────────────────────
    try:
        deadline = datetime.strptime(cfg["deadline"], "%Y-%m-%d").date()
        days_left = (deadline - date.today()).days
    except:
        days_left = "—"

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown('<p class="page-title">DASHBOARD</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">// Your execution reality — right now</p>', unsafe_allow_html=True)

    # ── Main goal hero ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="card-accent" style="padding:2rem;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem">
            <div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#4a4a7a;text-transform:uppercase;letter-spacing:2px;margin-bottom:0.5rem">
                    PRIMARY OBJECTIVE
                </div>
                <div style="font-family:'Bebas Neue',cursive;font-size:2.2rem;letter-spacing:3px;color:#e8e8f0;line-height:1">
                    {cfg['main_goal_label']}
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;color:#7c6afc;margin-top:0.5rem">
                    KES {total_earned:,.0f} <span style="color:#4a4a7a;font-size:0.8rem">/ {goal:,.0f}</span>
                </div>
            </div>
            <div style="text-align:center">
                <div style="font-family:'Bebas Neue',cursive;font-size:4rem;color:{'#ff4d6d' if isinstance(days_left,int) and days_left < 30 else '#3dffc0'};line-height:1">
                    {days_left}
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;text-transform:uppercase;letter-spacing:1.5px">
                    DAYS LEFT
                </div>
            </div>
        </div>
        <div style="margin-top:1.5rem">
            <div class="progress-label">
                <span>PROGRESS TO FREEDOM</span>
                <span class="accent-purple">{pct:.2f}%</span>
            </div>
            <div style="height:14px;background:#1e1e3a;border-radius:999px;overflow:hidden;position:relative">
                <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#7c6afc,#3dffc0);border-radius:999px;position:relative">
                    <div style="position:absolute;right:0;top:0;height:100%;width:20px;background:rgba(255,255,255,0.3);border-radius:999px;filter:blur(4px)"></div>
                </div>
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;margin-top:0.4rem">
                KES {goal - total_earned:,.0f} remaining to target
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sub-goals ────────────────────────────────────────────────────────────
    st.markdown("### Sub-Goals")
    sub_progress = dm.get_sub_goal_progress()
    cols = st.columns(len(sub_progress)) if sub_progress else []
    colors = ["#7c6afc", "#3dffc0", "#ff8c42", "#4dc9ff", "#ff4d6d"]
    for i, (sg, saved) in enumerate(sub_progress):
        p2 = min(100, (saved / sg["amount"]) * 100) if sg["amount"] > 0 else 0
        with cols[i] if cols else st.container():
            st.markdown(f"""
            <div class="card" style="text-align:center">
                <div style="font-size:2rem;margin-bottom:0.5rem">{sg.get('icon','🎯')}</div>
                <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:0.9rem;color:#e8e8f0;margin-bottom:0.25rem">
                    {sg['label']}
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:{colors[i % len(colors)]};margin-bottom:0.75rem">
                    KES {saved:,.0f} / {sg['amount']:,.0f}
                </div>
                <div style="height:8px;background:#1e1e3a;border-radius:999px;overflow:hidden">
                    <div style="height:100%;width:{p2}%;background:{colors[i % len(colors)]};border-radius:999px"></div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#4a4a7a;margin-top:0.4rem">{p2:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Daily performance panel ───────────────────────────────────────────────
    st.markdown("### Today's Execution Panel")

    tasks_done = sum(1 for v in today.get("tasks", {}).values() if v)
    tasks_total = len(cfg["daily_tasks"])
    task_pct = int((tasks_done / tasks_total) * 100) if tasks_total > 0 else 0

    scripts = today.get("scripts_written", 0)
    script_target = cfg["daily_script_target"]
    outreach = today.get("outreach_sent", 0)
    outreach_target = cfg["daily_outreach_target"]

    # today's income
    today_income = sum(
        e["amount"] for e in dm.get_income_entries()
        if e.get("date") == date.today().isoformat()
    )

    c1, c2, c3, c4 = st.columns(4)
    def metric_html(value, label, color="#7c6afc"):
        return f"""
        <div class="metric-box">
            <div class="metric-value" style="color:{color}">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """

    with c1:
        st.markdown(metric_html(f"{scripts}/{script_target}", "SCRIPTS TODAY", "#3dffc0"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_html(f"{outreach}/{outreach_target}", "OUTREACH SENT", "#4dc9ff"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_html(f"KES {today_income:,.0f}", "EARNED TODAY", "#ff8c42"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_html(f"{task_pct}%", "TASKS DONE", "#7c6afc"), unsafe_allow_html=True)

    # ── Quick daily input ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚡ Quick Update")

    col1, col2 = st.columns(2)
    with col1:
        scripts_in = st.number_input("Scripts written today", min_value=0, value=scripts, step=1)
    with col2:
        outreach_in = st.number_input("Outreach messages sent today", min_value=0, value=outreach, step=1)

    if st.button("💾 Save Daily Progress"):
        today["scripts_written"] = scripts_in
        today["outreach_sent"] = outreach_in
        dm.save_day(today)
        st.success("Daily progress saved!")
        st.rerun()

    # ── Missed tasks from yesterday ──────────────────────────────────────────
    from datetime import timedelta
    yesterday_key = (date.today() - timedelta(days=1)).isoformat()
    yesterday = dm.get_day(yesterday_key)
    missed = [
        t for t in cfg["daily_tasks"]
        if not yesterday.get("tasks", {}).get(t, False)
    ]
    if missed:
        st.markdown("---")
        st.markdown("### ⚠️ Carried Forward from Yesterday")
        for t in missed:
            st.markdown(f"<div class='card' style='padding:0.75rem 1rem;border-left:3px solid #ff8c42;color:#ff8c42;font-family:JetBrains Mono,monospace;font-size:0.85rem'>↩ {t}</div>", unsafe_allow_html=True)
