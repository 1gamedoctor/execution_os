import streamlit as st
from datetime import date, timedelta
import json

def render(dm):
    st.markdown('<p class="page-title">ANALYTICS</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">// Patterns reveal truth. Data drives improvement.</p>', unsafe_allow_html=True)

    cfg = dm.get_config()
    all_days = dm.get_all_days()
    entries = dm.get_income_entries()

    if not entries and not all_days:
        st.markdown('<div class="card" style="color:#4a4a7a;text-align:center;font-family:JetBrains Mono,monospace;padding:2rem">No data yet. Start logging income and tasks to see analytics.</div>', unsafe_allow_html=True)
        return

    # ── Income trend (last 30 days) ───────────────────────────────────────────
    st.markdown("### 📈 Income — Last 30 Days")
    days30 = [(date.today() - timedelta(days=i)) for i in range(29, -1, -1)]
    daily_income = {}
    for e in entries:
        d = e.get("date", "")
        daily_income[d] = daily_income.get(d, 0) + e["amount"]

    income_vals = [daily_income.get(d.isoformat(), 0) for d in days30]
    income_labels = [d.strftime("%b %d") for d in days30]

    # Build a simple bar chart with HTML/CSS
    max_val = max(income_vals) if max(income_vals) > 0 else 1
    bars_html = '<div style="display:flex;align-items:flex-end;gap:3px;height:160px;background:#12121f;border-radius:8px;padding:1rem;border:1px solid #1e1e3a;overflow-x:auto">'
    for i, (val, label) in enumerate(zip(income_vals, income_labels)):
        h = int((val / max_val) * 130)
        color = "#7c6afc" if val == max_val else "#3dffc0" if val > 0 else "#1e1e3a"
        tip = f"KES {val:,.0f}" if val > 0 else "—"
        bars_html += f'''
        <div title="{label}: {tip}" style="display:flex;flex-direction:column;align-items:center;flex:1;min-width:8px;cursor:default">
            <div style="width:100%;background:{color};height:{h}px;border-radius:3px 3px 0 0;transition:height 0.3s"></div>
        </div>'''
    bars_html += "</div>"
    st.markdown(bars_html, unsafe_allow_html=True)

    # Summary stats
    total_30 = sum(income_vals)
    days_with_income = sum(1 for v in income_vals if v > 0)
    avg_per_active_day = total_30 / days_with_income if days_with_income else 0

    c1, c2, c3 = st.columns(3)
    def mbox(val, label, color="#7c6afc"):
        return f'<div class="metric-box"><div class="metric-value" style="font-size:1.4rem;color:{color}">{val}</div><div class="metric-label">{label}</div></div>'
    with c1: st.markdown(mbox(f"KES {total_30:,.0f}", "30-DAY TOTAL", "#3dffc0"), unsafe_allow_html=True)
    with c2: st.markdown(mbox(f"{days_with_income}", "ACTIVE EARNING DAYS", "#ff8c42"), unsafe_allow_html=True)
    with c3: st.markdown(mbox(f"KES {avg_per_active_day:,.0f}", "AVG PER ACTIVE DAY", "#7c6afc"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Task completion rate ───────────────────────────────────────────────────
    st.markdown("### ✅ Task Completion — Last 14 Days")
    tasks = cfg["daily_tasks"]
    days14 = [(date.today() - timedelta(days=i)) for i in range(13, -1, -1)]

    completion_rates = []
    for d in days14:
        day_data = all_days.get(d.isoformat(), {})
        done = sum(1 for t in tasks if day_data.get("tasks", {}).get(t, False))
        rate = int((done / len(tasks)) * 100) if tasks else 0
        completion_rates.append(rate)

    bars2 = '<div style="display:flex;align-items:flex-end;gap:6px;height:140px;background:#12121f;border-radius:8px;padding:1rem;border:1px solid #1e1e3a">'
    for d, rate in zip(days14, completion_rates):
        h = int((rate / 100) * 110)
        color = "#3dffc0" if rate >= 80 else "#ff8c42" if rate >= 50 else "#ff4d6d" if rate > 0 else "#1e1e3a"
        bars2 += f'''
        <div title="{d.strftime('%b %d')}: {rate}%" style="display:flex;flex-direction:column;align-items:center;flex:1;cursor:default">
            <div style="font-family:JetBrains Mono,monospace;font-size:0.55rem;color:#4a4a7a;margin-bottom:2px">{rate}%</div>
            <div style="width:100%;background:{color};height:{h}px;border-radius:3px 3px 0 0"></div>
            <div style="font-family:JetBrains Mono,monospace;font-size:0.55rem;color:#4a4a7a;margin-top:3px;writing-mode:vertical-rl;transform:rotate(180deg)">{d.strftime("%d")}</div>
        </div>'''
    bars2 += "</div>"
    st.markdown(bars2, unsafe_allow_html=True)

    avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
    perfect_days = sum(1 for r in completion_rates if r == 100)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(mbox(f"{avg_completion:.0f}%", "AVG DAILY COMPLETION", "#7c6afc"), unsafe_allow_html=True)
    with c2: st.markdown(mbox(f"{perfect_days}", "PERFECT DAYS (14D)", "#3dffc0"), unsafe_allow_html=True)
    with c3:
        streak = 0
        for d in reversed(days14):
            day_data = all_days.get(d.isoformat(), {})
            done = sum(1 for t in tasks if day_data.get("tasks", {}).get(t, False))
            rate = int((done / len(tasks)) * 100) if tasks else 0
            if rate >= 80:
                streak += 1
            else:
                break
        st.markdown(mbox(f"{streak} days", "CURRENT STREAK (≥80%)", "#ff8c42"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Scripts & Outreach trend ──────────────────────────────────────────────
    st.markdown("### ✍️ Scripts & Outreach — Last 14 Days")
    script_target = cfg["daily_script_target"]
    outreach_target = cfg["daily_outreach_target"]

    rows = []
    for d in days14:
        day_data = all_days.get(d.isoformat(), {})
        rows.append({
            "date": d.strftime("%d %b"),
            "scripts": day_data.get("scripts_written", 0),
            "outreach": day_data.get("outreach_sent", 0),
        })

    table_html = """
    <div class="card" style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-family:'JetBrains Mono',monospace;font-size:0.75rem">
    <thead>
    <tr>
    <th style="text-align:left;padding:0.5rem;color:#4a4a7a;border-bottom:1px solid #1e1e3a">DATE</th>
    <th style="text-align:center;padding:0.5rem;color:#4a4a7a;border-bottom:1px solid #1e1e3a">SCRIPTS</th>
    <th style="text-align:center;padding:0.5rem;color:#4a4a7a;border-bottom:1px solid #1e1e3a">OUTREACH</th>
    <th style="text-align:center;padding:0.5rem;color:#4a4a7a;border-bottom:1px solid #1e1e3a">SCRIPT GOAL</th>
    <th style="text-align:center;padding:0.5rem;color:#4a4a7a;border-bottom:1px solid #1e1e3a">OUTREACH GOAL</th>
    </tr>
    </thead><tbody>
    """
    for r in rows:
        sc = r["scripts"]
        oc = r["outreach"]
        sc_color = "#3dffc0" if sc >= script_target else "#ff4d6d" if sc > 0 else "#4a4a7a"
        oc_color = "#3dffc0" if oc >= outreach_target else "#ff4d6d" if oc > 0 else "#4a4a7a"
        table_html += f"""
        <tr>
        <td style="padding:0.5rem;color:#8888aa;border-bottom:1px solid #0d0d1a">{r['date']}</td>
        <td style="text-align:center;padding:0.5rem;color:{sc_color};border-bottom:1px solid #0d0d1a">{sc}</td>
        <td style="text-align:center;padding:0.5rem;color:{oc_color};border-bottom:1px solid #0d0d1a">{oc}</td>
        <td style="text-align:center;padding:0.5rem;color:#4a4a7a;border-bottom:1px solid #0d0d1a">{script_target}</td>
        <td style="text-align:center;padding:0.5rem;color:#4a4a7a;border-bottom:1px solid #0d0d1a">{outreach_target}</td>
        </tr>
        """
    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── Income by source ──────────────────────────────────────────────────────
    st.markdown("### 💸 Income by Source")
    source_totals = {}
    for e in entries:
        s = e.get("source", "Other")
        source_totals[s] = source_totals.get(s, 0) + e["amount"]

    if source_totals:
        grand = sum(source_totals.values())
        colors = ["#7c6afc", "#3dffc0", "#ff8c42", "#4dc9ff", "#ff4d6d", "#b388ff", "#69f0ae"]
        for i, (src, amt) in enumerate(sorted(source_totals.items(), key=lambda x: -x[1])):
            pct = (amt / grand) * 100
            c = colors[i % len(colors)]
            st.markdown(f"""
            <div style="margin-bottom:0.6rem">
                <div style="display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:0.75rem;margin-bottom:0.3rem">
                    <span style="color:#8888aa">{src}</span>
                    <span style="color:{c}">KES {amt:,.0f} ({pct:.1f}%)</span>
                </div>
                <div style="height:8px;background:#1e1e3a;border-radius:999px;overflow:hidden">
                    <div style="height:100%;width:{pct}%;background:{c};border-radius:999px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
