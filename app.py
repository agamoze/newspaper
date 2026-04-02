"""
My News Button 📰
On-demand news fetcher from selected Indian publishers.
"""

import time
import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
from urllib.parse import quote

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Ai Meets the Morning Paper",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DEFAULT SETTINGS
# ─────────────────────────────────────────────
DEFAULT_PUBLISHERS = [
    "The Indian Express",
    "Hindustan Times",
    "The Hindu",
    "Economic Times",
]

DEFAULT_KEYWORDS = [
    "AI",
    "Indian stock market",
    "Fortune 500",
    "solar energy",
    "wind energy",
    "hydro energy",
    "tidal energy",
    "renewable energy",
    "Latest Technology",
    "Agentic AI",
]

DEFAULT_ARTICLES_PER_TOPIC = 8   # Changed to per-topic for better grouping

PUBLISHER_SOURCE_MAP = {
    "The Indian Express": "indianexpress.com",
    "Hindustan Times": "hindustantimes.com",
    "The Hindu": "thehindu.com",
    "Economic Times": "economictimes.indiatimes.com",
}

# ─────────────────────────────────────────────
# CUSTOM CSS – Light, Professional & Eye-Friendly
# ─────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: #F9F7F0 !important;
    }
    
    .main-title {
        text-align: center;
        font-family: 'Georgia', 'Times New Roman', serif;
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
        font-weight: 400;
    }
    
    /* Smaller rectangular button with rounded corners */
    div[data-testid="stButton"] > button {
        display: block;
        margin: 0 auto 2rem auto;
        background-color: #2C5F4A !important;
        color: white !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        padding: 0.7rem 2.8rem !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(44, 95, 74, 0.3);
    }
    
    div[data-testid="stButton"] > button:hover {
        background-color: #234B3A !important;
        transform: translateY(-1px);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    
    publishers_raw = st.text_area(
        "Publishers (one per line)",
        value="\n".join(DEFAULT_PUBLISHERS),
        height=140,
    )
    publishers = [p.strip() for p in publishers_raw.splitlines() if p.strip()]
    
    st.markdown("---")
    
    keywords_raw = st.text_area(
        "Topics / Keywords (one per line)",
        value="\n".join(DEFAULT_KEYWORDS),
        height=260,
    )
    keywords = [k.strip() for k in keywords_raw.splitlines() if k.strip()]
    
    st.markdown("---")
    
    articles_per_topic = st.slider(
        "Max articles per topic",
        min_value=3,
        max_value=15,
        value=DEFAULT_ARTICLES_PER_TOPIC,
        step=1,
    )

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
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

def fetch_all_articles(publishers: list, keywords: list, max_per_topic: int):
    all_articles = []
    seen_titles = set()
    
    for pub in publishers:
        source_domain = PUBLISHER_SOURCE_MAP.get(pub)
        if not source_domain:
            continue
            
        for keyword in keywords:
            url = build_rss_url(keyword, source_domain)
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:max_per_topic * 2]:  # Fetch extra then dedup
                    title = getattr(entry, "title", "").strip()
                    if not title or title.lower() in seen_titles:
                        continue
                    
                    seen_titles.add(title.lower())
                    
                    all_articles.append({
                        "Topic": keyword,
                        "Title": title,
                        "Link": getattr(entry, "link", "#"),
                        "Publisher": pub,
                        "Published": parse_published_time(entry),
                    })
            except:
                continue
    
    # Convert to DataFrame and sort: first by Topic, then newest first
    df = pd.DataFrame(all_articles)
    if not df.empty:
        df = df.sort_values(by=["Topic", "Published"], ascending=[True, False])
        # Limit per topic
        df = df.groupby("Topic").head(max_per_topic)
    
    return df

# ─────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">My News Button 📰</div>', unsafe_allow_html=True)
st.markdown('<div class="greeting">Hi mate, welcome again</div>', unsafe_allow_html=True)

_, col_btn, _ = st.columns([1, 2, 1])
with col_btn:
    fetch_clicked = st.button("Fetch Latest News", use_container_width=True)

# ─────────────────────────────────────────────
# FETCH & DISPLAY
# ─────────────────────────────────────────────
if fetch_clicked:
    if not publishers or not keywords:
        st.warning("Please add at least one publisher and one keyword in the sidebar.")
    else:
        progress_bar = st.progress(0, text="Fetching latest news from your publishers...")
        
        df = fetch_all_articles(publishers, keywords, articles_per_topic)
        
        progress_bar.progress(100, text="Done!")
        time.sleep(0.3)
        progress_bar.empty()
        
        if df.empty:
            st.info("No matching articles found right now. Try adjusting your topics or publishers.")
        else:
            total = len(df)
            st.success(f"✅ Found {total} relevant articles")
            
            # Make Title column clickable using LinkColumn
            st.dataframe(
                df,
                column_config={
                    "Title": st.column_config.LinkColumn(
                        "Article Title",
                        display_text=None,   # Shows full title as link text
                        help="Click to read the full article"
                    ),
                    "Link": None,   # Hide the raw URL column
                },
                use_container_width=True,
                hide_index=True,
            )
            
            st.caption("Articles are grouped and sorted by Topic • Newest first within each topic")
else:
    st.info("Click the button above to fetch the latest news tailored to your topics.")

st.caption("Built with Streamlit • Powered by Google News RSS")
