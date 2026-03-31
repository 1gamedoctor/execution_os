import streamlit as st
from datetime import date

def render(dm):
    cfg = dm.get_config()
    today_data = dm.get_day()
    task_states = today_data.get("tasks", {})

    st.markdown('<p class="page-title">DAILY TASKS</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">// Check off what you execute. Nothing disappears.</p>', unsafe_allow_html=True)

    tasks = cfg["daily_tasks"]
    done = sum(1 for t in tasks if task_states.get(t, False))
    pct = int((done / len(tasks)) * 100) if tasks else 0

    st.markdown(f"""
    <div class="card-accent" style="display:flex;align-items:center;gap:2rem;flex-wrap:wrap">
        <div>
            <div style="font-family:'Bebas Neue',cursive;font-size:3.5rem;color:#7c6afc;line-height:1">{done}/{len(tasks)}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;text-transform:uppercase;letter-spacing:1.5px">Tasks Completed</div>
        </div>
        <div style="flex:1;min-width:200px">
            <div class="progress-label">
                <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#4a4a7a">COMPLETION</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#7c6afc">{pct}%</span>
            </div>
            <div style="height:10px;background:#1e1e3a;border-radius:999px;overflow:hidden">
                <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#7c6afc,#3dffc0);border-radius:999px"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ✅ Today's Checklist")
    st.markdown(f"*{date.today().strftime('%A, %d %B %Y')}*")

    updated = dict(task_states)
    for i, task in enumerate(tasks):
        checked = task_states.get(task, False)
        new_val = st.checkbox(task, value=checked, key=f"task_{i}")
        updated[task] = new_val

    if st.button("💾 Save Task Progress"):
        today_data["tasks"] = updated
        dm.save_day(today_data)
        st.success("Tasks saved!")
        st.rerun()

    # ── Weekly task view ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📅 Task History (Last 7 Days)")

    from datetime import timedelta
    all_days = dm.get_all_days()
    days_range = [(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]

    table_html = """
    <div class="card" style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-family:'JetBrains Mono',monospace;font-size:0.72rem">
    <thead>
    <tr>
    <th style="text-align:left;padding:0.5rem;color:#4a4a7a;border-bottom:1px solid #1e1e3a">TASK</th>
    """
    for d in days_range:
        table_html += f'<th style="padding:0.5rem;color:#4a4a7a;border-bottom:1px solid #1e1e3a;text-align:center">{d.strftime("%a %d")}</th>'
    table_html += "</tr></thead><tbody>"

    for task in tasks:
        table_html += f'<tr><td style="padding:0.5rem 0.5rem 0.5rem 0;color:#8888aa;white-space:nowrap;border-bottom:1px solid #0d0d1a">{task[:35]}{"…" if len(task)>35 else ""}</td>'
        for d in days_range:
            day_data = all_days.get(d.isoformat(), {})
            done_t = day_data.get("tasks", {}).get(task, False)
            cell_color = "#3dffc0" if done_t else "#ff4d6d"
            symbol = "✓" if done_t else "✗"
            bg = "#1a2e1a" if done_t else "#2e1a1a"
            table_html += f'<td style="text-align:center;padding:0.5rem;border-bottom:1px solid #0d0d1a"><span style="color:{cell_color};background:{bg};padding:0.15rem 0.4rem;border-radius:4px">{symbol}</span></td>'
        table_html += "</tr>"

    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)
