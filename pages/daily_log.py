import streamlit as st
from datetime import date

MOODS = ["🔥 On Fire", "💪 Solid", "😐 Okay", "😔 Low Energy", "🤒 Rough Day"]

def render(dm):
    st.markdown('<p class="page-title">DAILY LOG</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">// Your growth timeline. Every day recorded.</p>', unsafe_allow_html=True)

    # ── New entry ─────────────────────────────────────────────────────────────
    st.markdown("### 📝 Log Today's Entry")
    with st.form("log_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            entry_date = st.date_input("Date", value=date.today())
        with col2:
            mood = st.selectbox("Energy Level", MOODS)

        accomplished = st.text_area("What did you accomplish today?", height=100, placeholder="Be specific. What got done?")
        learned = st.text_area("What did you learn?", height=80, placeholder="Any insight, skill, or lesson from today...")
        earned = st.number_input("Money earned today (KES)", min_value=0.0, step=100.0, format="%.2f")
        improve = st.text_area("What could be improved tomorrow?", height=80, placeholder="One honest thing to do better...")
        submitted = st.form_submit_button("📓 Save Log Entry")

        if submitted:
            if not accomplished.strip():
                st.warning("Please fill in what you accomplished.")
            else:
                dm.add_log_entry({
                    "date": entry_date.isoformat(),
                    "mood": mood,
                    "accomplished": accomplished,
                    "learned": learned,
                    "earned": earned,
                    "improve": improve,
                })
                st.success("✅ Log entry saved!")
                st.rerun()

    st.markdown("---")

    # ── Past entries ──────────────────────────────────────────────────────────
    st.markdown("### 📚 Growth Timeline")
    entries = dm.get_log_entries()

    if not entries:
        st.markdown('<div class="card" style="color:#4a4a7a;text-align:center;font-family:JetBrains Mono,monospace;padding:2rem">No log entries yet. Start recording your journey.</div>', unsafe_allow_html=True)
        return

    for i, e in enumerate(entries):
        mood_color = {
            "🔥 On Fire": "#ff8c42",
            "💪 Solid": "#3dffc0",
            "😐 Okay": "#4dc9ff",
            "😔 Low Energy": "#8888aa",
            "🤒 Rough Day": "#ff4d6d",
        }.get(e.get("mood", ""), "#7c6afc")

        with st.expander(f"{e.get('mood','')}  {e['date']}  —  KES {e.get('earned',0):,.0f} earned", expanded=(i == 0)):
            col1, col2 = st.columns([5, 1])
            with col1:
                if e.get("accomplished"):
                    st.markdown(f"""
                    <div style="margin-bottom:0.75rem">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.3rem">ACCOMPLISHED</div>
                        <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;color:#e8e8f0;line-height:1.6">{e['accomplished']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                if e.get("learned"):
                    st.markdown(f"""
                    <div style="margin-bottom:0.75rem">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.3rem">LEARNED</div>
                        <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;color:#8888aa;line-height:1.6">{e['learned']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                if e.get("improve"):
                    st.markdown(f"""
                    <div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a4a7a;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:0.3rem">IMPROVE TOMORROW</div>
                        <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;color:#ff8c42;line-height:1.6">{e['improve']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑", key=f"logdel_{i}"):
                    dm.delete_log_entry(i)
                    st.rerun()
