"""
data_manager.py — Supabase-backed persistence with local JSON fallback
                  + automatic migration from local → Supabase on first connect.

Supabase setup (one-time, ~5 min):
  1. Create free project at https://supabase.com
  2. SQL Editor → run supabase_schema.sql
  3. Project Settings → API → copy Project URL + anon public key
  4. Add to .streamlit/secrets.toml:
       [supabase]
       url = "https://xxxx.supabase.co"
       key = "eyJ..."
     OR paste the same block into Streamlit Cloud → Settings → Secrets.

Migration behaviour:
  - First time the app starts with Supabase credentials, it checks whether
    Supabase already has data for each key (config / days / income / log).
  - For any key that is EMPTY in Supabase but has data in local JSON,
    the local data is pushed up automatically — once, silently.
  - A sentinel key "migration_done" is written so the check never repeats.
"""

import json, os
from datetime import date, datetime

# ── Local JSON helpers ────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def _path(name): return os.path.join(DATA_DIR, f"{name}.json")

def _load_local(name, default):
    os.makedirs(DATA_DIR, exist_ok=True)
    p = _path(name)
    if os.path.exists(p):
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            pass
    return default

def _save_local(name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_path(name), "w") as f:
        json.dump(data, f, indent=2)

# Keep bare _load/_save aliases (settings.py uses them)
_load = _load_local
_save = _save_local

# ── Supabase lazy init ────────────────────────────────────────────────────────
_sb = None

def _get_sb():
    global _sb
    if _sb is not None:
        return _sb
    try:
        import streamlit as st
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        from supabase import create_client
        _sb = create_client(url, key)
    except Exception:
        pass
    return _sb

def _use_supabase():
    return _get_sb() is not None

# ── Supabase read / write ─────────────────────────────────────────────────────
def _sb_get(key, default):
    try:
        res = _get_sb().table("kv_store").select("value").eq("id", key).execute()
        if res.data:
            return res.data[0]["value"]
        return default
    except Exception as e:
        print(f"[Supabase] GET '{key}': {e}")
        return default

def _sb_set(key, data):
    try:
        _get_sb().table("kv_store").upsert({
            "id": key,
            "value": data,
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()
    except Exception as e:
        print(f"[Supabase] SET '{key}': {e}")

def _sb_has(key):
    """Return True if the key exists and is not None/empty in Supabase."""
    try:
        res = _get_sb().table("kv_store").select("value").eq("id", key).execute()
        return bool(res.data)
    except Exception:
        return False

# ── Unified read / write ──────────────────────────────────────────────────────
def _get(name, default):
    return _sb_get(name, default) if _use_supabase() else _load_local(name, default)

def _set(name, data):
    if _use_supabase():
        _sb_set(name, data)
    else:
        _save_local(name, data)

# ── Auto-migration: local JSON → Supabase ─────────────────────────────────────
_MIGRATION_KEY = "migration_done"
_DATA_KEYS = ["config", "days", "income", "log"]

def _run_migration_if_needed():
    """
    Called once per app session when Supabase is available.
    Pushes any local JSON data that is missing from Supabase.
    Safe to call multiple times — the sentinel prevents repeat runs.
    """
    if not _use_supabase():
        return

    # Already migrated? Skip entirely.
    if _sb_has(_MIGRATION_KEY):
        return

    migrated = []
    for key in _DATA_KEYS:
        # Only migrate if Supabase has nothing for this key
        if _sb_has(key):
            continue

        # Read local file — skip if it doesn't exist or is empty/default
        local_path = _path(key)
        if not os.path.exists(local_path):
            continue
        try:
            with open(local_path) as f:
                local_data = json.load(f)
        except Exception:
            continue

        # Don't push empty containers
        if local_data in ({}, [], None):
            continue

        _sb_set(key, local_data)
        migrated.append(key)

    # Write sentinel so we never do this again
    _sb_set(_MIGRATION_KEY, {
        "migrated_at": datetime.utcnow().isoformat(),
        "keys_migrated": migrated,
    })

    return migrated  # callers can display this in the UI if desired

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "main_goal_amount": 20_000_000,
    "main_goal_label": "KES 20M Freedom Fund",
    "deadline": "2025-12-31",
    "daily_script_target": 3,
    "daily_outreach_target": 20,
    "sub_goals": [
        {"label": "High-Performance Laptop", "amount": 200_000, "icon": "💻"},
        {"label": "Premium Smartphone",      "amount": 150_000, "icon": "📱"},
        {"label": "Studio Setup",            "amount": 350_000, "icon": "🎙️"},
    ],
    "daily_tasks": [
        "Write scripts (daily target)",
        "Send outreach messages",
        "Client work / delivery",
        "Trading study (1hr)",
        "Content brainstorming",
        "End-of-day reflection",
        "Review analytics",
    ],
    "vision_images": [
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800",
        "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800",
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800",
        "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800",
        "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=800",
    ],
}

DEFAULT_DAY = {"scripts_written": 0, "outreach_sent": 0, "tasks": {}, "notes": ""}


# ── DataManager ───────────────────────────────────────────────────────────────
class DataManager:

    def __init__(self):
        # Attempt migration silently every time the manager is created.
        # In Streamlit this happens once per session.
        try:
            self._migrated_keys = _run_migration_if_needed() or []
        except Exception:
            self._migrated_keys = []

    # ── Storage info ─────────────────────────────────────────────────────────
    def is_cloud(self):
        return _use_supabase()

    def storage_label(self):
        return "☁️ Supabase" if _use_supabase() else "💾 Local JSON"

    def get_migrated_keys(self):
        """Returns list of keys that were just migrated this session (empty after first run)."""
        return self._migrated_keys

    # ── Config ────────────────────────────────────────────────────────────────
    def get_config(self):
        return _get("config", DEFAULT_CONFIG)

    def save_config(self, cfg):
        _set("config", cfg)

    # ── Daily state ───────────────────────────────────────────────────────────
    def _today_key(self):
        return date.today().isoformat()

    def get_day(self, day_key=None):
        if day_key is None:
            day_key = self._today_key()
        return self.get_all_days().get(day_key, {**DEFAULT_DAY, "tasks": {}})

    def save_day(self, data, day_key=None):
        if day_key is None:
            day_key = self._today_key()
        all_days = self.get_all_days()
        all_days[day_key] = data
        _set("days", all_days)

    def get_all_days(self):
        return _get("days", {})

    # ── Finance ───────────────────────────────────────────────────────────────
    def get_income_entries(self):
        return _get("income", [])

    def add_income(self, amount, source, note=""):
        entries = self.get_income_entries()
        entries.append({
            "date": date.today().isoformat(),
            "amount": amount,
            "source": source,
            "note": note,
            "timestamp": datetime.now().isoformat(),
        })
        _set("income", entries)

    def delete_income(self, idx):
        entries = self.get_income_entries()
        if 0 <= idx < len(entries):
            entries.pop(idx)
            _set("income", entries)

    def get_total_earned(self):
        return sum(e["amount"] for e in self.get_income_entries())

    def get_sub_goal_progress(self):
        cfg = self.get_config()
        total = self.get_total_earned()
        result, running = [], 0
        for sg in cfg["sub_goals"]:
            allocated = max(0, min(sg["amount"], total - running))
            running += allocated
            result.append((sg, allocated))
        return result

    # ── Daily log ─────────────────────────────────────────────────────────────
    def get_log_entries(self):
        return _get("log", [])

    def add_log_entry(self, entry: dict):
        entries = self.get_log_entries()
        entries.insert(0, {**entry, "timestamp": datetime.now().isoformat()})
        _set("log", entries)

    def delete_log_entry(self, idx):
        entries = self.get_log_entries()
        if 0 <= idx < len(entries):
            entries.pop(idx)
            _set("log", entries)
