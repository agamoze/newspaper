# 📰 My News Button — Setup & Deployment Guide

---

## What this app does

**My News Button** fetches the latest news from 4 top Indian publishers
(Indian Express, Hindustan Times, The Hindu, Economic Times) filtered by
topics you care about (AI, renewable energy, stock market, etc.).

It uses **Google News RSS feeds** — completely free, no API key needed.

---

## Files in this project

```
news_app/
├── app.py            ← The entire Streamlit application
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## Run Locally (Step-by-Step)

### Step 1 — Install Python
Make sure you have **Python 3.9 or newer** installed.
Check by running:
```bash
python --version
```
Download from https://python.org if needed.

### Step 2 — Create a virtual environment (recommended)
```bash
cd news_app
python -m venv venv

# Activate it:
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the app
```bash
streamlit run app.py
```

Your browser opens automatically at **http://localhost:8501**

### Step 5 — Use the app
1. Edit publishers, keywords, and article count in the left sidebar.
2. Click **"Fetch Latest News"**.
3. Articles appear as cards grouped by publisher.
4. Click any article title to open it in a new tab.

---

## Deploy FREE on Streamlit Cloud

Streamlit Cloud hosts your app for free at a public URL. No credit card needed.

### Step 1 — Push code to GitHub
1. Create a free account at https://github.com
2. Create a new repository (e.g., `my-news-button`)
3. Upload both `app.py` and `requirements.txt` to the repo
   (use "Add file → Upload files" on the GitHub website)

### Step 2 — Sign in to Streamlit Cloud
Go to https://streamlit.io/cloud and sign in with your GitHub account.

### Step 3 — Deploy
1. Click **"New app"**
2. Choose your GitHub repo
3. Set **Main file path** to `app.py`
4. Click **"Deploy!"**

Your app will be live in ~60 seconds at a URL like:
```
https://your-username-my-news-button-app-xxxx.streamlit.app
```

---

## How to Customise

### Add a new publisher
In `app.py`, find `PUBLISHER_SOURCE_MAP` and add an entry:
```python
PUBLISHER_SOURCE_MAP = {
    ...
    "NDTV":  "ndtv.com",
    "Mint":  "livemint.com",
}
```
Then type the display name into the sidebar's publisher text area.

### Change default keywords or publishers
Edit `DEFAULT_KEYWORDS` or `DEFAULT_PUBLISHERS` near the top of `app.py`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| No articles appear | Google News may throttle; wait 30 s and retry |
| Publisher not found | Name in sidebar must match a key in `PUBLISHER_SOURCE_MAP` |
| Streamlit Cloud fails | Ensure `requirements.txt` is in the same folder as `app.py` |

---

## Dependencies

| Package | Why |
|---|---|
| `streamlit >= 1.32` | Web app framework — handles UI, layout, sidebar |
| `feedparser >= 6.0` | Parses Google News RSS XML into Python objects |

No API keys. No paid services. 100% free to run and deploy.
