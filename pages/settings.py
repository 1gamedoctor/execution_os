import streamlit as st
import json
from datetime import date

ICONS = ["💻", "📱", "🎙️", "🎹", "🚗", "🏠", "✈️", "📷", "🖥️", "⌚", "🎯", "💎"]

def render(dm):
    cfg = dm.get_config()

    st.markdown('<p class="page-title">SETTINGS</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">// Calibrate the system to your ambitions.</p>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Main Goal",
        "📋 Daily Tasks",
        "🏆 Sub-Goals",
        "🖼️ Vision Images",
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
            st.success("✅ Saved!")
            st.rerun()

    # ── Tab 2: Daily Tasks ────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Daily Task List")
        st.markdown("*One task per line.*")
        tasks_text = st.text_area(
            "Tasks", value="\n".join(cfg["daily_tasks"]),
            height=300, label_visibility="collapsed"
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
        sub_goals = cfg["sub_goals"].copy()

        for i, sg in enumerate(sub_goals):
            st.markdown(f"**Sub-Goal {i+1}**")
            c1, c2, c3, c4 = st.columns([1, 4, 3, 1])
            with c1:
                icon = st.selectbox(
                    "Icon", ICONS,
                    index=ICONS.index(sg.get("icon", "🎯")) if sg.get("icon", "🎯") in ICONS else 0,
                    key=f"icon_{i}", label_visibility="collapsed"
                )
            with c2:
                label = st.text_input("Label", value=sg["label"], key=f"sg_label_{i}", label_visibility="collapsed")
            with c3:
                amount = st.number_input(
                    "Amount (KES)", min_value=0.0, value=float(sg["amount"]),
                    step=1000.0, format="%.0f", key=f"sg_amt_{i}", label_visibility="collapsed"
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
            "Image URLs", value="\n".join(cfg.get("vision_images", [])),
            height=300, label_visibility="collapsed"
        )
        if st.button("💾 Save Vision Images"):
            new_images = [u.strip() for u in images_text.split("\n") if u.strip()]
            cfg["vision_images"] = new_images
            dm.save_config(cfg)
            st.success(f"✅ Saved {len(new_images)} images!")
            st.rerun()

    # ── Supabase connection ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ☁️ Supabase Connection")

    from data_manager import save_supabase_creds, delete_supabase_creds, get_saved_creds

    is_connected = dm.is_cloud()

    if is_connected:
        st.success("✅ Supabase is connected — your data is saved to the cloud.")
        if st.button("🔌 Disconnect Supabase"):
            delete_supabase_creds()
            st.success("Disconnected. Restart the app for changes to take effect.")
            st.rerun()
    else:
        st.warning("⚠️ Not connected — data resets when Streamlit sleeps the app.")

    st.markdown("Paste your Supabase credentials below to connect:")

    saved = get_saved_creds()
    input_url = st.text_input(
        "Project URL",
        value=saved.get("url", ""),
        placeholder="https://abcdefghijkl.supabase.co"
    )
    input_key = st.text_input(
        "Anon / Public Key",
        value=saved.get("key", ""),
        placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        type="password"
    )

    if st.button("🔗 Save & Connect"):
        if not input_url.strip() or not input_key.strip():
            st.error("Both fields are required.")
        else:
            # Test the connection first
            try:
                from supabase import create_client
                test = create_client(input_url.strip(), input_key.strip())
                test.table("kv_store").select("id").limit(1).execute()
                save_supabase_creds(input_url, input_key)
                st.success("✅ Connected! Restarting app...")
                st.rerun()
            except Exception as e:
                err = str(e)
                if "kv_store" in err or "relation" in err.lower():
                    st.error("❌ Connected but kv_store table is missing. Run supabase_schema.sql in your Supabase SQL Editor first.")
                elif "401" in err or "Invalid API key" in err:
                    st.error("❌ Invalid key. Make sure you copied the anon/public key, not the service_role key.")
                else:
                    st.error(f"❌ Could not connect: {err}")

    # ── Danger zone ───────────────────────────────────────────────────────────
    st.markdown("---")
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
                from data_manager import _set
                _set("income", [])
                st.success("Income data cleared.")
                st.rerun()

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📦 Export Data")
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
