import json, os
from datetime import date, datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def _path(name): return os.path.join(DATA_DIR, f"{name}.json")

def _load(name, default):
    os.makedirs(DATA_DIR, exist_ok=True)
    p = _path(name)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return default

def _save(name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_path(name), "w") as f:
        json.dump(data, f, indent=2)

# ── Default config ───────────────────────────────────────────────────────────
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

class DataManager:
    def get_config(self):
        return _load("config", DEFAULT_CONFIG)

    def save_config(self, cfg):
        _save("config", cfg)

    # ── Daily state ──────────────────────────────────────────────────────────
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

    # ── Finance ──────────────────────────────────────────────────────────────
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

    # ── Daily log entries ────────────────────────────────────────────────────
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
