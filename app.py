"""
My News Button 📰
Articles displayed in clean tabular format, grouped by Topic
"""

import time
import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
from urllib.parse import quote

# Page Config
st.set_page_config(
    page_title="My News Button",
    page_icon="📰",
    layout="wide",
)

# Default Settings
DEFAULT_PUBLISHERS = [
    "The Indian Express", "Hindustan Times", "The Hindu", "Economic Times"
]

DEFAULT_KEYWORDS = [
    "AI", "Indian stock market", "Fortune 500", "solar energy", 
    "wind energy", "hydro energy", "tidal energy", "renewable energy",
    "Latest Technology", "Agentic AI"
]

PUBLISHER_SOURCE_MAP = {
    "The Indian Express": "indianexpress.com",
    "Hindustan Times": "hindustantimes.com",
    "The Hindu": "thehindu.com",
    "Economic Times": "economictimes.indiatimes.com",
}

# Custom CSS - Light Theme + Clean Table
st.markdown("""
<style>
    [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #F9F7F0 !important;
    }
    .main-title {
        text-align: center;
        font-family: 'Georgia', serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #1F1F1F;
        margin-bottom: 0.5rem;
    }
    .greeting {
        text-align: center;
        font-size: 1.25rem;
        color: #2C2C2C;
        margin-bottom: 2rem;
    }
    /* Button */
    div[data-testid="stButton"] > button {
        display: block;
        margin: 0 auto 2rem auto;
        background-color: #2C5F4A !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.75rem 3rem !important;
        border-radius: 10px !important;
    }
    /* Clean Table Styling */
    .article-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    .article-table th {
        background-color: #F4F1E9;
        padding: 14px 12px;
        text-align: left;
        font-weight: 600;
        color: #1F1F1F;
        border-bottom: 2px solid #E5E0D5;
    }
    .article-table td {
        padding: 14px 12px;
        border-bottom: 1px solid #EDE9DF;
        vertical-align: top;
    }
    .article-table a {
        color: #1F1F1F;
        text-decoration: none;
        font-weight: 500;
    }
    .article-table a:hover {
        color: #2C5F4A;
        text-decoration: underline;
    }
    .topic-header {
        background-color: #F4F1E9;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 25px 0 12px 0;
        font-size: 1.15rem;
        font-weight: 600;
        color: #1F1F1F;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    publishers_raw = st.text_area("Publishers (one per line)", "\n".join(DEFAULT_PUBLISHERS), height=140)
    publishers = [p.strip() for p in publishers_raw.splitlines() if p.strip()]

    keywords_raw = st.text_area("Topics / Keywords (one per line)", "\n".join(DEFAULT_KEYWORDS), height=260)
    keywords = [k.strip() for k in keywords_raw.splitlines() if k.strip()]

    max_articles = st.slider("Max articles per topic", 3, 15, 8)

# Helper Functions
def build_rss_url(keyword: str, source_domain: str) -> str:
    query = f"site:{source_domain} {keyword}"
    encoded = quote(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"

def parse_published_time(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6])
            return dt.strftime("%d %b %Y, %I:%M %p")
        except:
            pass
    return "—"

def fetch_articles(publishers, keywords, max_articles):
    articles = []
    seen = set()
    
    for pub in publishers:
        domain = PUBLISHER_SOURCE_MAP.get(pub)
        if not domain:
            continue
        for kw in keywords:
            url = build_rss_url(kw, domain)
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:20]:   # Fetch more then limit
                    title = getattr(entry, "title", "").strip()
                    if not title or title.lower() in seen:
                        continue
                    seen.add(title.lower())
                    
                    link = getattr(entry, "link", "#")
                    # Clean Google redirect link if present
                    if "news.google.com" in link and "/articles/" in link:
                        # Try to extract real link if possible, else keep as is
                        link = link
                    
                    articles.append({
                        "Topic": kw,
                        "Title": title,
                        "Link": link,
                        "Publisher": pub,
                        "Published": parse_published_time(entry)
                    })
            except:
                continue
    
    df = pd.DataFrame(articles)
    if not df.empty:
        df = df.sort_values(by=["Topic", "Published"], ascending=[True, False])
        df = df.groupby("Topic").head(max_articles)
    return df

# Main UI
st.markdown('<div class="main-title">My News Button 📰</div>', unsafe_allow_html=True)
st.markdown('<div class="greeting">Hi mate, welcome again</div>', unsafe_allow_html=True)

_, col, _ = st.columns([1, 2, 1])
with col:
    fetch_clicked = st.button("Fetch Latest News", use_container_width=True)

if fetch_clicked:
    if not publishers or not keywords:
        st.warning("⚠️ Please add at least one publisher and one topic in the sidebar.")
    else:
        progress_bar = st.progress(0, text="Fetching latest news...")
        
        df = fetch_articles(publishers, keywords, max_articles)
        
        progress_bar.progress(100, text="Completed!")
        time.sleep(0.4)
        progress_bar.empty()

        if df.empty:
            st.info("No articles found. Try different keywords.")
        else:
            st.success(f"✅ Found {len(df)} articles")

            # Display grouped by Topic with clean HTML tables
            for topic, group in df.groupby("Topic"):
                st.markdown(f'<div class="topic-header">📌 {topic} — {len(group)} articles</div>', 
                           unsafe_allow_html=True)
                
                # Build clean HTML table
                html = """
                <table class="article-table">
                    <thead>
                        <tr>
                            <th>Article Title</th>
                            <th>Publisher</th>
                            <th>Published</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for _, row in group.iterrows():
                    html += f"""
                        <tr>
                            <td><a href="{row['Link']}" target="_blank" rel="noopener">{row['Title']}</a></td>
                            <td>{row['Publisher']}</td>
                            <td>{row['Published']}</td>
                        </tr>
                    """
                html += "</tbody></table><br>"
                
                st.markdown(html, unsafe_allow_html=True)

else:
    st.info("Click the button above to fetch news sorted by topic.")

st.caption("Articles are grouped by Topic • Click on any title to open the full article")
