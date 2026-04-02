"""
My News Button 📰
A simple on-demand news fetcher for your favorite Indian publishers.
"""

import time
import streamlit as st
import feedparser
from datetime import datetime
from urllib.parse import quote

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="My News Button",
    page_icon="📰",
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

DEFAULT_ARTICLES_PER_PUBLISHER = 10

# Publisher name → domain for Google News "site:" filter
PUBLISHER_SOURCE_MAP = {
    "The Indian Express": "indianexpress.com",
    "Hindustan Times": "hindustantimes.com",
    "The Hindu": "thehindu.com",
    "Economic Times": "economictimes.indiatimes.com",
}

# ─────────────────────────────────────────────
# CUSTOM CSS – Light Theme with your exact colors
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background color */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: #F9F6C4 !important;
    }
    
    /* Title and text colors */
    h1, h2, h3, p, label {
        color: #000000 !important;
    }
    
    /* Professional font for title */
    .main-title {
        text-align: center;
        font-family: 'Georgia', 'Times New Roman', serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #000000;
        margin-bottom: 0.5rem;
    }
    
    /* Greeting */
    .greeting {
        text-align: center;
        font-size: 1.25rem;
        color: #000000;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Fetch Button Styling */
    div[data-testid="stButton"] > button {
        display: block;
        margin: 0 auto 2rem auto;
        background-color: #2F6B3F !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.75rem 2.5rem !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(47, 107, 63, 0.3);
        transition: all 0.2s ease;
    }
    
    div[data-testid="stButton"] > button:hover {
        background-color: #265832 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(47, 107, 63, 0.4);
    }
    
    /* Article Cards */
    .article-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .card-title a {
        color: #000000 !important;
        text-decoration: none;
        font-weight: 600;
    }
    
    .card-title a:hover {
        color: #2F6B3F !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f5f0b8 !important;
    }
    
    /* Progress bar text */
    .stProgress > label {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR SETTINGS
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
        "Keywords / Topics (one per line)",
        value="\n".join(DEFAULT_KEYWORDS),
        height=260,
    )
    keywords = [k.strip() for k in keywords_raw.splitlines() if k.strip()]
    
    st.markdown("---")
    
    articles_per_pub = st.slider(
        "Max articles per publisher",
        min_value=3,
        max_value=20,
        value=DEFAULT_ARTICLES_PER_PUBLISHER,
        step=1,
    )

# ─────────────────────────────────────────────
# HELPER FUNCTIONS (same as before - no change needed)
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
    return getattr(entry, "published", "Time unavailable")

def fetch_articles_for_publisher(publisher_name: str, kw_list: list, max_articles: int) -> list:
    source_domain = PUBLISHER_SOURCE_MAP.get(publisher_name)
    if not source_domain:
        return []
    
    seen_titles = set()
    articles = []
    
    for keyword in kw_list:
        url = build_rss_url(keyword, source_domain)
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = getattr(entry, "title", "").strip()
                if not title or title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())
                
                articles.append({
                    "title": title,
                    "link": getattr(entry, "link", "#"),
                    "publisher": publisher_name,
                    "time": parse_published_time(entry),
                })
        except:
            continue
    
    # Sort by time (newest first) - simple fallback
    articles = articles[:max_articles]
    return articles

# ─────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────
# Title + Greeting
st.markdown('<div class="main-title">My News Button 📰</div>', unsafe_allow_html=True)
st.markdown('<div class="greeting">Hi mate, welcome again</div>', unsafe_allow_html=True)

# Fetch Button (smaller, rounded, green)
_, col_btn, _ = st.columns([1, 2, 1])
with col_btn:
    fetch_clicked = st.button("Fetch Latest News", use_container_width=True)

# ─────────────────────────────────────────────
# FETCH LOGIC
# ─────────────────────────────────────────────
if fetch_clicked:
    if not publishers:
        st.warning("Please add at least one publisher in the sidebar.")
    elif not keywords:
        st.warning("Please add at least one keyword in the sidebar.")
    else:
        all_results = {}
        total_count = 0
        
        # Progress bar while fetching
        progress_text = "Fetching latest news from your publishers..."
        progress_bar = st.progress(0, text=progress_text)
        
        for i, pub in enumerate(publishers):
            # Update progress
            progress = int((i + 1) / len(publishers) * 100)
            progress_bar.progress(progress, text=f"{progress_text} ({pub})")
            
            articles = fetch_articles_for_publisher(pub, keywords, articles_per_pub)
            all_results[pub] = articles
            total_count += len(articles)
            
            time.sleep(0.3)  # Small delay for realistic progress feel
        
        progress_bar.empty()  # Remove progress bar after completion
        
        # Results
        if total_count > 0:
            st.success(f"✅ Found {total_count} articles across {len(publishers)} publisher(s)")
            
            for pub, articles in all_results.items():
                if articles:
                    st.markdown(f"### {pub} ({len(articles)} articles)")
                    for art in articles:
                        st.markdown(f"""
                        <div class="article-card">
                            <div class="card-title">
                                <a href="{art['link']}" target="_blank">{art['title']}</a>
                            </div>
                            <p style="color:#555; margin-top:8px;">
                                🗞️ {art['publisher']} • 🕒 {art['time']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No matching articles found right now. Try changing keywords or try again later.")
else:
    st.info("Click the button above to fetch the latest news.")

st.caption("Built with Streamlit • Powered by Google News RSS")
