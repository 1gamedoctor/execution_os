import streamlit as st
import json
from datetime import date

def render(dm):
    cfg = dm.get_config()

    st.markdown('<p class="page-title">SETTINGS</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">// Calibrate the system to your ambitions.</p>', unsafe_allow_html=True)

    # ── Storage status banner ─────────────────────────────────────────────────
    mode = dm.storage_label()
    is_supabase = "Supabase" in mode
    banner_color = "#1a2e1a" if is_supabase else "#2e1e0a"
    dot_color   = "#3dffc0"  if is_supabase else "#ff8c42"
    status_msg  = "Connected — your data persists forever." if is_supabase else "Not connected — data resets on container restart."
    st.markdown(f"""
    <div style="background:{banner_color};border:1px solid {dot_color}33;border-radius:10px;padding:0.9rem 1.25rem;
                display:flex;align-items:center;gap:0.75rem;margin-bottom:1.5rem">
        <div style="width:10px;height:10px;border-radius:50%;background:{dot_color};flex-shrink:0"></div>
        <div>
            <span style="font-family:'Space Grotesk',sans-serif;font-weight:600;color:{dot_color}">{mode}</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#8888aa;margin-left:0.75rem">{status_msg}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not is_supabase:
        with st.expander("⚡ How to connect Supabase (takes ~5 minutes)", expanded=True):
            st.markdown("""
**Step 1 — Create a free Supabase project**
- Go to [supabase.com](https://supabase.com) → New project
- Pick any region close to Kenya (e.g. `eu-west-1`)
- Wait ~2 minutes for it to spin up

**Step 2 — Run the schema**
- In your project: **SQL Editor → New query**
- Paste the entire contents of `supabase_schema.sql` (included in your zip)
- Click **Run**

**Step 3 — Copy your credentials**
- Go to **Project Settings → API**
- Copy: **Project URL** and **anon / public key**

**Step 4 — Add secrets to Streamlit Cloud**
- In your app on share.streamlit.io: **⋮ → Settings → Secrets**
- Paste this (replace with your real values):
```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key-here"
```
- Click **Save** → the app will reboot and show ☁️ Supabase above

**That's it.** All your data now lives in Supabase and survives forever.
""")

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Main Goal", "📋 Daily Tasks", "🏆 Sub-Goals", "🖼️ Vision Images"])

    # ── Tab 1: Main Goal ──────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Main Goal Configuration")
        new_label = st.text_input("Goal Label", value=cfg["main_goal_label"])
        new_amount = st.number_input("Goal Amount (KES)", min_value=1000.0, value=float(cfg["main_goal_amount"]), step=100000.0, format="%.0f")
        new_deadline = st.date_input("Deadline", value=date.fromisoformat(cfg["deadline"]))
        new_script_target = st.number_input("Daily Script Target", min_value=1, value=cfg["daily_script_target"], step=1)
        new_outreach_target = st.number_input("Daily Outreach Target", min_value=1, value=cfg["daily_outreach_target"], step=1)

        if st.button("💾 Save Main Goal Settings"):
            cfg["main_goal_label"] = new_label
            cfg["main_goal_amount"] = new_amount
            cfg["deadline"] = new_deadline.isoformat()
            cfg["daily_script_target"] = new_script_target
            cfg["daily_outreach_target"] = new_outreach_target
            dm.save_config(cfg)
            st.success("Main goal settings saved!")
            st.rerun()

    # ── Tab 2: Daily Tasks ────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Daily Task List")
        st.markdown("*One task per line. These appear on your daily checklist.*")

        tasks_text = st.text_area(
            "Tasks (one per line)",
            value="\n".join(cfg["daily_tasks"]),
            height=300,
        )

        if st.button("💾 Save Tasks"):
            new_tasks = [t.strip() for t in tasks_text.split("\n") if t.strip()]
            if new_tasks:
                cfg["daily_tasks"] = new_tasks
                dm.save_config(cfg)
                st.success(f"Saved {len(new_tasks)} tasks!")
                st.rerun()
            else:
                st.warning("Task list cannot be empty.")

    # ── Tab 3: Sub-Goals ──────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Sub-Goals")
        st.markdown("*These are layered targets within your main goal.*")

        sub_goals = cfg["sub_goals"].copy()
        ICONS = ["💻", "📱", "🎙️", "🎹", "🚗", "🏠", "✈️", "📷", "🖥️", "⌚", "🎯", "💎"]

        for i, sg in enumerate(sub_goals):
            st.markdown(f"**Sub-Goal {i+1}**")
            c1, c2, c3, c4 = st.columns([1, 4, 3, 1])
            with c1:
                icon = st.selectbox("Icon", ICONS, index=ICONS.index(sg.get("icon","🎯")) if sg.get("icon","🎯") in ICONS else 0, key=f"icon_{i}")
            with c2:
                label = st.text_input("Label", value=sg["label"], key=f"sg_label_{i}")
            with c3:
                amount = st.number_input("Amount (KES)", min_value=0.0, value=float(sg["amount"]), step=1000.0, format="%.0f", key=f"sg_amt_{i}")
            with c4:
                if st.button("🗑", key=f"sg_del_{i}"):
                    sub_goals.pop(i)
                    cfg["sub_goals"] = sub_goals
                    dm.save_config(cfg)
                    st.rerun()
            sub_goals[i] = {"label": label, "amount": amount, "icon": icon}

        if st.button("➕ Add Sub-Goal"):
            sub_goals.append({"label": "New Goal", "amount": 100000, "icon": "🎯"})
            cfg["sub_goals"] = sub_goals
            dm.save_config(cfg)
            st.rerun()

        if st.button("💾 Save Sub-Goals"):
            cfg["sub_goals"] = sub_goals
            dm.save_config(cfg)
            st.success("Sub-goals saved!")
            st.rerun()

    # ── Tab 4: Vision Images ──────────────────────────────────────────────────
    with tab4:
        st.markdown("### Vision Board Images")
        st.markdown("*Paste image URLs (one per line). Use Unsplash, Pexels, or any direct image URL.*")

        images_text = st.text_area(
            "Image URLs",
            value="\n".join(cfg.get("vision_images", [])),
            height=300,
        )

        if st.button("💾 Save Vision Images"):
            new_images = [u.strip() for u in images_text.split("\n") if u.strip()]
            cfg["vision_images"] = new_images
            dm.save_config(cfg)
            st.success(f"Saved {len(new_images)} images!")
            st.rerun()

    st.markdown("---")

    # ── Danger zone ───────────────────────────────────────────────────────────
    with st.expander("⚠️ Danger Zone"):
        st.warning("These actions cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Config to Defaults"):
                from data_manager import DEFAULT_CONFIG
                dm.save_config(DEFAULT_CONFIG)
                st.success("Config reset.")
                st.rerun()
        with col2:
            if st.button("🗑️ Clear All Income Data"):
                import json, os
                path = os.path.join(os.path.dirname(dm.__class__.__module__) if hasattr(dm.__class__.__module__, '__file__') else ".", "data", "income.json")
                # Use the internal save method
                from data_manager import _save
                _save("income", [])
                st.success("Income data cleared.")
                st.rerun()

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("### 📦 Export Data")
    export_data = {
        "config": dm.get_config(),
        "income": dm.get_income_entries(),
        "days": dm.get_all_days(),
        "log": dm.get_log_entries(),
    }
    st.download_button(
        label="⬇️ Download Full Backup (JSON)",
        data=json.dumps(export_data, indent=2),
        file_name=f"execution_os_backup_{date.today().isoformat()}.json",
        mime="application/json",
    )
