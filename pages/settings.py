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

        # ── Current status ────────────────────────────────────────────────────
        if is_supabase:
            st.success("✅ Supabase is connected and active. All your data is saved to the cloud.")
        else:
            st.warning("⚠️ Not connected. Data will reset when Streamlit sleeps the app.")

        st.markdown("---")

        # ── Step 1: Generate the secrets block ───────────────────────────────
        st.markdown("#### Step 1 — Enter your Supabase credentials")
        st.markdown(
            "Paste your values below. This generates the exact block you need to copy "
            "into Streamlit Cloud. Your credentials are **never saved** here — this is "
            "just a formatting helper."
        )

        input_url = st.text_input(
            "Supabase Project URL",
            placeholder="https://abcdefghijkl.supabase.co",
            help="Found in: Supabase Dashboard → Project Settings → API → Project URL"
        )
        input_key = st.text_input(
            "Supabase anon / public key",
            placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            type="password",
            help="Found in: Supabase Dashboard → Project Settings → API → anon public"
        )

        if input_url and input_key:
            secrets_block = f'[supabase]\nurl = "{input_url}"\nkey = "{input_key}"'
            st.markdown("#### ✅ Your secrets block — copy this:")
            st.code(secrets_block, language="toml")
            st.info(
                "👆 Copy the block above, then go to: **share.streamlit.io** → your app → "
                "**⋮ menu** → **Settings** → **Secrets** → paste it in → **Save**. "
                "The app will restart and connect automatically."
            )

            # ── Test the connection right now ─────────────────────────────────
            st.markdown("#### 🔌 Test connection before deploying")
            if st.button("Test these credentials now"):
                try:
                    from supabase import create_client
                    test_client = create_client(input_url, input_key)
                    # Try a real read against the kv_store table
                    test_client.table("kv_store").select("id").limit(1).execute()
                    st.success(
                        "✅ Connection successful! These credentials work and the "
                        "kv_store table exists. Go ahead and paste the block into "
                        "Streamlit Cloud Secrets."
                    )
                except Exception as e:
                    err = str(e)
                    if "kv_store" in err or "relation" in err.lower():
                        st.warning(
                            "⚠️ Connected to Supabase but the **kv_store table is missing**. "
                            "Go to Supabase → SQL Editor → paste and run `supabase_schema.sql`."
                        )
                    elif "Invalid API key" in err or "401" in err:
                        st.error("❌ Invalid API key. Double-check you copied the **anon public** key, not the service_role key.")
                    elif "invalid input syntax" in err.lower() or "hostname" in err.lower():
                        st.error("❌ Invalid Project URL. Make sure it starts with https:// and has no trailing slash.")
                    else:
                        st.error(f"❌ Connection failed: {err}")
        else:
            st.markdown(
                "<div style='font-family:JetBrains Mono,monospace;font-size:0.75rem;"
                "color:#4a4a7a;padding:1rem;background:#12121f;border-radius:8px;"
                "border:1px dashed #2d2d5e'>Fill in both fields above to generate "
                "your secrets block and test your connection.</div>",
                unsafe_allow_html=True
            )

        st.markdown("---")

        # ── Where to find credentials ─────────────────────────────────────────
        with st.expander("📍 Where to find these values in Supabase"):
            st.markdown("""
1. Go to [supabase.com](https://supabase.com) → open your project
2. Click the **gear icon** (Project Settings) in the bottom-left sidebar
3. Click **API** in the settings menu
4. You'll see:
   - **Project URL** — copy the full URL including `https://`
   - **Project API keys → anon public** — copy this key (NOT the `service_role` key)

Don't have a project yet? Create one free at [supabase.com](https://supabase.com) — takes 2 minutes.
""")

        with st.expander("🗄️ Setting up the database table (one-time)"):
            st.markdown("""
Before the app can save data to Supabase you need to create one table:

1. In your Supabase project → click **SQL Editor** → **New query**
2. Paste this SQL and click **Run**:
""")
            st.code("""
create table if not exists kv_store (
  id          text primary key,
  value       jsonb        not null,
  updated_at  timestamptz  not null default now()
);

alter table kv_store enable row level security;

create policy "Allow full access"
  on kv_store for all
  using (true) with check (true);
""", language="sql")
            st.markdown("You should see *'Success. No rows returned'*. Done — the table is ready.")

        with st.expander("📊 Supabase free tier — will I ever hit the limits?"):
            st.markdown("""
| Resource | Free limit | This app uses |
|----------|-----------|---------------|
| Database size | 500 MB | < 1 MB |
| API calls | 50,000 / month | < 500 / month |
| Projects | 2 free | 1 |
| Bandwidth | 5 GB | Negligible |

You will never hit any limit with this app.
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
