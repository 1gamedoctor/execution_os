# ⚡ Personal Execution OS

A Streamlit-powered productivity system that replaces motivation with consistency, clarity, and accountability.

## Quick Start

```bash
# 1. Install dependencies
pip install streamlit

# 2. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Deploy Online (Free)

### Option A — Streamlit Community Cloud (Recommended)
1. Push this folder to a GitHub repo
2. Go to https://share.streamlit.io
3. Connect your repo → select `app.py` → Deploy
4. Your app is live at a public URL (accessible on mobile too)

### Option B — Railway / Render
- Point to this repo, set start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Features

| Page | What it does |
|------|-------------|
| 🏠 Dashboard | Main goal progress bar, countdown, sub-goals, daily panel |
| ✅ Daily Tasks | Checklist, carry-forward of missed tasks, 7-day history grid |
| 💰 Finance | Log income, sub-goal allocation, income history |
| 📓 Daily Log | End-of-day journal entries with mood tracking |
| 📊 Analytics | Income trends, task completion rates, income by source |
| 🎯 Vision Board | Curated image slideshow + daily affirmation |
| ⚙️ Settings | Customize goal, deadline, tasks, sub-goals, vision images |

## Data Storage

All data is stored locally in `data/` as JSON files:
- `config.json` — your goals and settings
- `income.json` — all income entries
- `days.json` — daily scripts/outreach/task state
- `log.json` — daily journal entries

Use **Settings → Export** to download a full backup anytime.

## Customization

On first run, go to **Settings** and:
1. Set your main goal amount and deadline
2. Edit your daily task list
3. Add sub-goals (laptop, phone, etc.)
4. Paste vision board image URLs (Unsplash, Pexels work great)
