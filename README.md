# ⚡ Execution OS

A personal productivity dashboard built with Streamlit, backed by **Firebase Firestore** so all your data persists even when Streamlit Cloud puts the app to sleep.

---

## 🔥 Firebase Setup (one-time)

### 1. Create a Firebase project
1. Go to [console.firebase.google.com](https://console.firebase.google.com) and create a project (or use an existing one).
2. In the left sidebar → **Firestore Database** → **Create database**.  
   Choose *Production mode* and pick a region close to you (e.g. `europe-west1` for East Africa).

### 2. Generate a service-account key
1. In Firebase Console → ⚙️ **Project Settings** → **Service accounts** tab.
2. Click **Generate new private key** → **Generate key**.
3. A JSON file downloads — keep it safe, **never commit it to Git**.

### 3. Configure secrets

**Local development**  
Copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` and fill in the values from the downloaded JSON file.

**Streamlit Cloud**  
In your app's dashboard → **Settings** → **Secrets**, paste the same `[firebase]` block.

The key fields to copy from your downloaded JSON:

| secrets.toml key     | JSON field            |
|----------------------|-----------------------|
| `type`               | `type`                |
| `project_id`         | `project_id`          |
| `private_key_id`     | `private_key_id`      |
| `private_key`        | `private_key`         |
| `client_email`       | `client_email`        |
| `client_id`          | `client_id`           |
| `client_x509_cert_url` | `client_x509_cert_url` |

> **Tip:** The `private_key` value contains literal `\n` characters. In secrets.toml wrap it in double quotes and keep the `\n` sequences – they will be unescaped automatically.

---

## 🚀 Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📦 Deploying to Streamlit Cloud

1. Push this repo to GitHub (the `.gitignore` already excludes `secrets.toml` and `firebase_key.json`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select your repo.
3. In **Advanced settings → Secrets**, paste your `[firebase]` block.
4. Deploy!

Your data now lives in Firestore and will be there every time the app wakes up.

---

## 🗂 Data structure in Firestore

All documents live in the `execution_os` collection:

| Document  | Contents                                      |
|-----------|-----------------------------------------------|
| `config`  | Goals, targets, vision images, task templates |
| `days`    | Daily task completions keyed by `YYYY-MM-DD`  |
| `income`  | Array of income entries                       |
| `log`     | Array of daily log entries                    |
