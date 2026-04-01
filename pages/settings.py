import streamlit as st
import json
from datetime import date


def render(dm):
    cfg = dm.get_config()

    st.markdown('<p class="page-title">SETTINGS</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">// Calibrate the system to your ambitions.</p>', unsafe_allow_html=True)

    # ── Storage status banner ─────────────────────────────────────────────────
    is_supabase  = dm.is_cloud()
    mode         = dm.storage_label()
    banner_color = "#1a2e1a" if is_supabase else "#2e1e0a"
    dot_color    = "#3dffc0" if is_supabase else "#ff8c42"
    status_msg   = "Connected — data persists forever." if is_supabase \
                   else "Not connected — add Supabase secrets to persist data."

    st.markdown(f"""
    <div style="background:{banner_color};border:1px solid {dot_color}55;border-radius:10px;
                padding:0.9rem 1.25rem;display:flex;align-items:center;gap:0.75rem;margin-bottom:1.5rem">
        <div style="width:10px;height:10px;border-radius:50%;background:{dot_color};flex-shrink:0"></div>
        <div>
            <span style="font-family:'Space Grotesk',sans-serif;font-weight:600;color:{dot_color}">{mode}</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#8888aa;margin-left:0.75rem">{status_msg}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Main Goal",
        "📋 Daily Tasks",
        "🏆 Sub-Goals",
        "🖼️ Vision Images",
        "☁️ Supabase",
    ])

    # ── Tab 1: Main Goal ──────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Main Goal Configuration")
        new_label  = st.text_input("Goal Label", value=cfg["main_goal_label"])
        new_amount = st.number_input(
            "Goal Amount (KES)", min_value=1000.0,
            value=float(cfg["main_goal_amount"]), step=100000.0, format="%.0f"
        )
        new_deadline        = st.date_input("Deadline", value=date.fromisoformat(cfg["deadline"]))
        new_script_target   = st.number_input("Daily Script Target",   min_value=1, value=cfg["daily_script_target"],   step=1)
        new_outreach_target = st.number_input("Daily Outreach Target", min_value=1, value=cfg["daily_outreach_target"], step=1)

        if st.button("💾 Save Main Goal Settings"):
            cfg["main_goal_label"]       = new_label
            cfg["main_goal_amount"]      = new_amount
            cfg["deadline"]              = new_deadline.isoformat()
            cfg["daily_script_target"]   = new_script_target
            cfg["daily_outreach_target"] = new_outreach_target
            dm.save_config(cfg)
            st.success("✅ Main goal settings saved!")
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
                st.success(f"✅ Saved {len(new_tasks)} tasks!")
                st.rerun()
            else:
                st.warning("Task list cannot be empty.")

    # ── Tab 3: Sub-Goals ──────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Sub-Goals")
        st.markdown("*Layered targets within your main goal.*")

        sub_goals = cfg["sub_goals"].copy()
        ICONS = ["💻", "📱", "🎙️", "🎹", "🚗", "🏠", "✈️", "📷", "🖥️", "⌚", "🎯", "💎"]

        for i, sg in enumerate(sub_goals):
            st.markdown(f"**Sub-Goal {i+1}**")
            c1, c2, c3, c4 = st.columns([1, 4, 3, 1])
            with c1:
                icon = st.selectbox(
                    "Icon", ICONS,
                    index=ICONS.index(sg.get("icon", "🎯")) if sg.get("icon", "🎯") in ICONS else 0,
                    key=f"icon_{i}"
                )
            with c2:
                label = st.text_input("Label", value=sg["label"], key=f"sg_label_{i}")
            with c3:
                amount = st.number_input(
                    "Amount (KES)", min_value=0.0,
                    value=float(sg["amount"]), step=1000.0, format="%.0f",
                    key=f"sg_amt_{i}"
                )
            with c4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑", key=f"sg_del_{i}"):
                    sub_goals.pop(i)
                    cfg["sub_goals"] = sub_goals
                    dm.save_config(cfg)
                    st.rerun()
            sub_goals[i] = {"label": label, "amount": amount, "icon": icon}

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add Sub-Goal"):
                sub_goals.append({"label": "New Goal", "amount": 100_000, "icon": "🎯"})
                cfg["sub_goals"] = sub_goals
                dm.save_config(cfg)
                st.rerun()
        with col2:
            if st.button("💾 Save Sub-Goals"):
                cfg["sub_goals"] = sub_goals
                dm.save_config(cfg)
                st.success("✅ Sub-goals saved!")
                st.rerun()

    # ── Tab 4: Vision Images ──────────────────────────────────────────────────
    with tab4:
        st.markdown("### Vision Board Images")
        st.markdown("*Paste image URLs, one per line. Unsplash and Pexels work great.*")
        images_text = st.text_area(
            "Image URLs",
            value="\n".join(cfg.get("vision_images", [])),
            height=300,
        )
        if st.button("💾 Save Vision Images"):
            new_images = [u.strip() for u in images_text.split("\n") if u.strip()]
            cfg["vision_images"] = new_images
            dm.save_config(cfg)
            st.success(f"✅ Saved {len(new_images)} images!")
            st.rerun()

    # ── Tab 5: Supabase ───────────────────────────────────────────────────────
    with tab5:
        st.markdown("### ☁️ Supabase — Persistent Cloud Storage")
        st.markdown("Connect Supabase so your data survives Streamlit Cloud sleep/restarts.")

        if is_supabase:
            st.success("✅ Supabase is connected and active. All data is being saved to the cloud.")
            st.markdown("Your connection is configured via Streamlit Cloud's Secrets panel. To update credentials, follow Step 4 below.")
        else:
            st.warning("⚠️ Not connected. Without Supabase, data resets when Streamlit sleeps the app.")

        st.markdown("---")

        st.markdown("""
#### Step 1 — Create a free Supabase project
- Go to [supabase.com](https://supabase.com) → sign up → **New project**
- Give it any name (e.g. `execution-os`), set a database password
- Pick the region closest to you — **eu-west-1** (Ireland) is closest to Kenya
- Wait about 2 minutes for it to provision

#### Step 2 — Create the database table
- In your project: click **SQL Editor** in the left sidebar → **New query**
- Paste the entire contents of `supabase_schema.sql` (included in your zip)
- Click **Run** — you should see *"Success. No rows returned"*

#### Step 3 — Get your credentials
- Click **Project Settings** (gear icon, bottom-left) → **API**
- Copy two values:
  - **Project URL** — looks like `https://abcdefgh.supabase.co`
  - **anon / public key** — long string starting with `eyJ...`

#### Step 4 — Add secrets to Streamlit Cloud
- Go to [share.streamlit.io](https://share.streamlit.io)
- Find your app → click **⋮ (three dots)** → **Settings** → **Secrets**
- Paste this block, replacing with your real values:
""")

        st.code("""[supabase]
url = "https://your-project-id.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." """, language="toml")

        st.markdown("""
- Click **Save** — the app restarts automatically
- Come back to this tab — the banner at the top of Settings should turn **green**

#### Step 5 — Verify migration (if you had existing data)
- On first load after connecting, a green toast notification will appear:
  *"☁️ Migrated local data to Supabase: config, income, days, log"*
- That means all your previous entries are now safely in the cloud
""")

        st.markdown("---")
        st.markdown("#### Supabase Free Tier Limits")
        st.markdown("""
| Resource | Free limit | Your usage |
|----------|-----------|------------|
| Database size | 500 MB | < 1 MB (JSON blobs) |
| API requests | 50,000 / month | < 500 / month |
| Projects | 2 | 1 |
| Bandwidth | 5 GB | Negligible |

You will **never** hit the free tier limits with this app.
""")

    # ── Danger zone ───────────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("⚠️ Danger Zone — irreversible actions"):
        st.warning("These actions cannot be undone. Data will be permanently deleted from wherever it is stored (Supabase or local).")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Config to Defaults"):
                from data_manager import DEFAULT_CONFIG
                dm.save_config(DEFAULT_CONFIG)
                st.success("Config reset to defaults.")
                st.rerun()
        with col2:
            if st.button("🗑️ Clear All Income Data"):
                from data_manager import _set
                _set("income", [])
                st.success("All income data cleared.")
                st.rerun()

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📦 Export Data")
    st.markdown("*Download a full backup of all your data as a JSON file.*")
    export_data = {
        "config": dm.get_config(),
        "income": dm.get_income_entries(),
        "days":   dm.get_all_days(),
        "log":    dm.get_log_entries(),
    }
    st.download_button(
        label="⬇️ Download Full Backup (JSON)",
        data=json.dumps(export_data, indent=2),
        file_name=f"execution_os_backup_{date.today().isoformat()}.json",
        mime="application/json",
    )
