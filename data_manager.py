"""
data_manager.py  –  Firebase Firestore backend for Execution OS
----------------------------------------------------------------
All data lives in Firestore so it persists across Streamlit Cloud
sleep/wake cycles.

Firestore structure:
  execution_os/config   → config document
  execution_os/income   → {_data: [...]}
  execution_os/log      → {_data: [...]}
  execution_os/days     → {_data: {<YYYY-MM-DD>: {...}, ...}}

Setup (one-time):
  1. Go to https://console.firebase.google.com → create/open a project.
  2. Firestore Database → Create database (production mode is fine).
  3. Project Settings → Service accounts → Generate new private key.
     Save the downloaded JSON somewhere safe – never commit it.
  4. In Streamlit Cloud → App settings → Secrets, add:

       [firebase]
       type                        = "service_account"
       project_id                  = "YOUR_PROJECT_ID"
       private_key_id              = "..."
       private_key                 = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
       client_email                = "..."
       client_id                   = "..."
       auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
       token_uri                   = "https://oauth2.googleapis.com/token"
       auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
       client_x509_cert_url        = "..."

  5. For local dev create .streamlit/secrets.toml with the same block,
     OR set GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase_key.json.
"""

import os
from datetime import date, datetime

import streamlit as st

# ── Firebase init ─────────────────────────────────────────────────────────────

def _get_db():
    """Return a cached Firestore client, initialising Firebase on first call."""
    import firebase_admin
    from firebase_admin import credentials, firestore

    if not firebase_admin._apps:
        if "firebase" in st.secrets:
            cred_dict = dict(st.secrets["firebase"])
            # Streamlit stores multiline values with literal \n – unescape them
            if "private_key" in cred_dict:
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(cred_dict)
        else:
            key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "firebase_key.json")
            cred = credentials.Certificate(key_path)

        firebase_admin.initialize_app(cred)

    return firestore.client()


_COL = "execution_os"


def _doc_ref(name: str):
    return _get_db().collection(_COL).document(name)


def _load(name: str, default):
    doc = _doc_ref(name).get()
    if doc.exists:
        return doc.to_dict().get("_data", default)
    return default


def _save(name: str, data):
    _doc_ref(name).set({"_data": data})


# ── Default config ────────────────────────────────────────────────────────────

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

DEFAULT_DAY = {
    "scripts_written": 0,
    "outreach_sent": 0,
    "tasks": {},
    "notes": "",
}


# ── DataManager ───────────────────────────────────────────────────────────────

class DataManager:

    def get_config(self):
        return _load("config", DEFAULT_CONFIG)

    def save_config(self, cfg):
        _save("config", cfg)

    # ── Daily state ───────────────────────────────────────────────────────────

    def _today_key(self):
        return date.today().isoformat()

    def get_day(self, day_key=None):
        if day_key is None:
            day_key = self._today_key()
        all_days = _load("days", {})
        return all_days.get(day_key, {**DEFAULT_DAY, "tasks": {}})

    def save_day(self, data, day_key=None):
        if day_key is None:
            day_key = self._today_key()
        all_days = _load("days", {})
        all_days[day_key] = data
        _save("days", all_days)

    def get_all_days(self):
        return _load("days", {})

    # ── Finance ───────────────────────────────────────────────────────────────

    def get_income_entries(self):
        return _load("income", [])

    def add_income(self, amount, source, note=""):
        entries = self.get_income_entries()
        entries.append({
            "date": date.today().isoformat(),
            "amount": amount,
            "source": source,
            "note": note,
            "timestamp": datetime.now().isoformat(),
        })
        _save("income", entries)

    def delete_income(self, idx):
        entries = self.get_income_entries()
        if 0 <= idx < len(entries):
            entries.pop(idx)
            _save("income", entries)

    def get_total_earned(self):
        return sum(e["amount"] for e in self.get_income_entries())

    def get_sub_goal_progress(self):
        """Returns list of (sub_goal_dict, amount_saved) tuples."""
        cfg = self.get_config()
        total = self.get_total_earned()
        result = []
        running = 0
        for sg in cfg["sub_goals"]:
            needed = sg["amount"]
            allocated = max(0, min(needed, total - running))
            running += allocated
            result.append((sg, allocated))
        return result

    # ── Daily log entries ─────────────────────────────────────────────────────

    def get_log_entries(self):
        return _load("log", [])

    def add_log_entry(self, entry: dict):
        entries = self.get_log_entries()
        entries.insert(0, {**entry, "timestamp": datetime.now().isoformat()})
        _save("log", entries)

    def delete_log_entry(self, idx):
        entries = self.get_log_entries()
        if 0 <= idx < len(entries):
            entries.pop(idx)
            _save("log", entries)
