"""
My News Button 📰
─────────────────────────────────────────────────────────────
A Streamlit app that fetches the latest news from top Indian
publishers on topics you care about.

How it works:
  • For each publisher + keyword, it queries Google News RSS
    (site:domain keyword) and parses the results with feedparser.
  • Articles are deduplicated, sorted newest-first, and capped
    at the user's requested count per publisher.
─────────────────────────────────────────────────────────────
"""

import time
import streamlit as st
import feedparser
from datetime import datetime
from urllib.parse import quote

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be the very first st call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="My News Button",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DEFAULT SETTINGS  – edit these to change defaults
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

# Maps publisher display names → their domain (used in Google News site: filter)
# To add a new publisher, add its name and domain here.
PUBLISHER_SOURCE_MAP = {
    "The Indian Express": "indianexpress.com",
    "Hindustan Times":    "hindustantimes.com",
    "The Hindu":          "thehindu.com",
    "Economic Times":     "economictimes.indiatimes.com",
}

# ─────────────────────────────────────────────
# CUSTOM CSS  – dark editorial aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

/* Design tokens */
:root {
    --bg:        #0d0f14;
    --surface:   #161a24;
    --border:    #252a38;
    --accent:    #e8b84b;
    --accent2:   #4b8be8;
    --text:      #e8e8e8;
    --muted:     #7a7f95;
    --success:   #3ecf8e;
    --radius:    12px;
}

/* ── App background ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stTextArea label {
    color: var(--muted) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header        { visibility: hidden; }
[data-testid="stToolbar"]        { display: none; }

/* ── Hero section ── */
.hero {
    text-align: center;
    padding: 2.5rem 0 1.2rem;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2rem, 5vw, 3.4rem);
    font-weight: 900;
    background: linear-gradient(135deg, var(--accent) 0%, #f5d88a 50%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -1px;
    line-height: 1.15;
}
.hero p {
    color: var(--muted);
    font-size: 0.9rem;
    margin-top: 0.5rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Fetch button ── */
div[data-testid="stButton"] > button {
    display: block;
    margin: 0 auto;
    background: linear-gradient(135deg, #e8b84b, #f5d88a) !important;
    color: #0d0f14 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.05em;
    padding: 0.85rem 3rem !important;
    border: none !important;
    border-radius: 50px !important;
    cursor: pointer;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    box-shadow: 0 4px 24px rgba(232,184,75,0.35);
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(232,184,75,0.55) !important;
    background: linear-gradient(135deg, #f5c84b, #ffe17a) !important;
}
div[data-testid="stButton"] > button:active { transform: translateY(0); }

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.8rem 0;
}

/* ── Success banner ── */
.success-banner {
    background: rgba(62,207,142,0.10);
    border: 1px solid rgba(62,207,142,0.35);
    border-radius: var(--radius);
    padding: 0.75rem 1.5rem;
    color: var(--success);
    font-size: 0.92rem;
    font-weight: 500;
    text-align: center;
    margin-bottom: 1rem;
}

/* ── Stats pills ── */
.stats-bar {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 2rem;
}
.stat-pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 50px;
    padding: 0.3rem 1rem;
    font-size: 0.8rem;
    color: var(--muted);
}
.stat-pill span { color: var(--accent); font-weight: 600; }

/* ── Publisher header ── */
.pub-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin: 2.2rem 0 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--border);
}
.pub-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
    box-shadow: 0 0 8px rgba(232,184,75,0.6);
}
.pub-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text);
}
.pub-count {
    margin-left: auto;
    font-size: 0.75rem;
    color: var(--muted);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 50px;
    padding: 0.2rem 0.8rem;
}

/* ── Article card ── */
.article-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin-bottom: 0.7rem;
    transition: border-color 0.2s ease, transform 0.2s ease;
    position: relative;
    overflow: hidden;
}
.article-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--accent), var(--accent2));
    border-radius: 3px 0 0 3px;
    opacity: 0;
    transition: opacity 0.2s ease;
}
.article-card:hover {
    border-color: rgba(232,184,75,0.5);
    transform: translateX(4px);
}
.article-card:hover::before { opacity: 1; }

.card-title a {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.97rem;
    color: var(--text) !important;
    text-decoration: none;
    line-height: 1.55;
}
.card-title a:hover { color: var(--accent) !important; }

.card-meta {
    display: flex;
    gap: 0.9rem;
    margin-top: 0.55rem;
    flex-wrap: wrap;
    align-items: center;
}
.meta-chip {
    font-size: 0.71rem;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 0.25rem;
}
.keyword-tag {
    background: rgba(232,184,75,0.12);
    color: var(--accent);
    border: 1px solid rgba(232,184,75,0.28);
    border-radius: 4px;
    padding: 0.13rem 0.5rem;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}

/* ── Empty / idle states ── */
.empty-state {
    text-align: center;
    padding: 3.5rem 1rem;
    color: var(--muted);
}
.empty-state .icon { font-size: 3.2rem; margin-bottom: 0.5rem; }
.empty-state p { font-size: 1rem; line-height: 1.7; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR  – user-editable settings
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    # --- Publishers ---
    st.markdown("**📰 Publishers**")
    publishers_raw = st.text_area(
        "One publisher per line",
        value="\n".join(DEFAULT_PUBLISHERS),
        height=130,
        key="publishers_input",
        help=(
            "Publisher names must match keys in PUBLISHER_SOURCE_MAP "
            "inside app.py. Add new ones there too."
        ),
    )
    publishers = [p.strip() for p in publishers_raw.splitlines() if p.strip()]

    st.markdown("---")

    # --- Keywords ---
    st.markdown("**🔍 Keywords / Topics**")
    keywords_raw = st.text_area(
        "One keyword per line",
        value="\n".join(DEFAULT_KEYWORDS),
        height=260,
        key="keywords_input",
    )
    keywords = [k.strip() for k in keywords_raw.splitlines() if k.strip()]

    st.markdown("---")

    # --- Article count ---
    articles_per_pub = st.slider(
        "Articles per publisher",
        min_value=3,
        max_value=30,
        value=DEFAULT_ARTICLES_PER_PUBLISHER,
        step=1,
    )

    st.markdown("---")
    st.markdown(
        "<small style='color:#4a5068'>Built with Streamlit + Google News RSS · "
        "No API key required</small>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def build_rss_url(keyword: str, source_domain: str) -> str:
    """
    Build a Google News RSS URL filtered by keyword AND source domain.

    Google News supports the 'site:' operator in its RSS search endpoint,
    so we use:  site:domain.com keyword
    """
    query = f"site:{source_domain} {keyword}"
    encoded = quote(query)
    return (
        f"https://news.google.com/rss/search"
        f"?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
    )


def parse_published_time(entry) -> str:
    """
    Return a human-friendly published time from a feedparser entry.
    feedparser normalises the time into 'published_parsed' (time.struct_time).
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6])
            return dt.strftime("%d %b %Y, %I:%M %p")
        except Exception:
            pass
    # Fall back to the raw string if parsing fails
    return getattr(entry, "published", "Time unavailable")


def detect_keyword(title: str, summary: str, kw_list: list) -> str:
    """
    Return the first keyword found in the article title or summary.
    Case-insensitive. Falls back to empty string if none match.
    """
    combined = (title + " " + summary).lower()
    for kw in kw_list:
        if kw.lower() in combined:
            return kw
    return ""


def fetch_articles_for_publisher(
    publisher_name: str,
    kw_list: list,
    max_articles: int,
) -> list:
    """
    Fetch and deduplicate articles for one publisher across all keywords.

    Steps:
      1. Look up the domain for this publisher.
      2. For each keyword, build the RSS URL and parse it.
      3. Deduplicate by title (case-insensitive).
      4. Sort newest-first and return up to max_articles.
    """
    source_domain = PUBLISHER_SOURCE_MAP.get(publisher_name)
    if not source_domain:
        # Publisher not in our map – skip gracefully
        return []

    seen_titles: set = set()
    articles: list = []

    for keyword in kw_list:
        url = build_rss_url(keyword, source_domain)
        try:
            feed = feedparser.parse(url)
        except Exception:
            # Network error for this keyword – skip and continue
            continue

        for entry in feed.entries:
            title   = getattr(entry, "title",   "").strip()
            link    = getattr(entry, "link",    "#")
            summary = getattr(entry, "summary", "")

            # Skip blank or duplicate titles
            title_key = title.lower()
            if not title or title_key in seen_titles:
                continue
            seen_titles.add(title_key)

            matched_kw = detect_keyword(title, summary, kw_list) or keyword

            articles.append({
                "title":    title,
                "link":     link,
                "publisher": publisher_name,
                "time":     parse_published_time(entry),
                "time_raw": getattr(entry, "published_parsed", None),
                "keyword":  matched_kw,
            })

    # Sort newest-first; articles without a parsed time go to the end
    articles.sort(
        key=lambda a: a["time_raw"] or time.gmtime(0),
        reverse=True,
    )

    return articles[:max_articles]


def render_article_card(article: dict):
    """Render a single article as an HTML card injected via st.markdown."""
    title   = article["title"]
    link    = article["link"]
    pub     = article["publisher"]
    t       = article["time"]
    keyword = article["keyword"]

    st.markdown(f"""
    <div class="article-card">
        <div class="card-title">
            <a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a>
        </div>
        <div class="card-meta">
            <span class="meta-chip">🗞&nbsp;{pub}</span>
            <span class="meta-chip">🕐&nbsp;{t}</span>
            {"<span class='keyword-tag'>" + keyword + "</span>" if keyword else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN PAGE LAYOUT
# ─────────────────────────────────────────────

# Hero header
st.markdown("""
<div class="hero">
    <h1>📰 My News Button</h1>
    <p>Your curated Indian news digest · powered by Google News RSS</p>
</div>
""", unsafe_allow_html=True)

# Centre the big button using Streamlit columns
_, col_btn, _ = st.columns([1, 2, 1])
with col_btn:
    fetch_clicked = st.button("🚀 Fetch Latest News", use_container_width=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FETCH + RENDER  (only runs when button is clicked)
# ─────────────────────────────────────────────
if fetch_clicked:

    # Validate that the user has entered publishers and keywords
    if not publishers:
        st.warning("⚠️  Please add at least one publisher in the sidebar.")
    elif not keywords:
        st.warning("⚠️  Please add at least one keyword in the sidebar.")
    else:
        all_results: dict = {}
        total_count = 0

        # Spinner while fetching from Google News RSS
        with st.spinner("Fetching the latest news for you… this may take a moment ☕"):
            for pub in publishers:
                articles = fetch_articles_for_publisher(pub, keywords, articles_per_pub)
                all_results[pub] = articles
                total_count += len(articles)

        # ── Success or empty state ──────────────────────────
        if total_count > 0:
            # Green success banner
            st.markdown(
                f'<div class="success-banner">'
                f'✅ Found <strong>{total_count}</strong> article'
                f'{"s" if total_count != 1 else ""} across '
                f'<strong>{len(publishers)}</strong> publisher'
                f'{"s" if len(publishers) != 1 else ""}'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Per-publisher stat pills
            pills = "".join(
                f'<div class="stat-pill">{pub}: <span>{len(arts)}</span></div>'
                for pub, arts in all_results.items()
            )
            st.markdown(f'<div class="stats-bar">{pills}</div>', unsafe_allow_html=True)

            # ── Render each publisher's articles ───────────
            for pub, articles in all_results.items():
                count_label = f"{len(articles)} article{'s' if len(articles) != 1 else ''}"
                st.markdown(f"""
                <div class="pub-header">
                    <div class="pub-dot"></div>
                    <div class="pub-name">{pub}</div>
                    <div class="pub-count">{count_label}</div>
                </div>
                """, unsafe_allow_html=True)

                if articles:
                    for art in articles:
                        render_article_card(art)
                else:
                    st.markdown("""
                    <div class="empty-state" style="padding:1.5rem">
                        <div class="icon">🔍</div>
                        <p>No matching articles found from this publisher right now.</p>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            # Nothing was found across all publishers/keywords
            st.markdown("""
            <div class="empty-state">
                <div class="icon">🗞️</div>
                <p><strong>No articles found.</strong><br>
                Try adjusting your keywords or publishers in the sidebar,<br>
                or wait a moment and try again.</p>
            </div>
            """, unsafe_allow_html=True)

else:
    # Idle state shown before the button is clicked
    st.markdown("""
    <div class="empty-state">
        <div class="icon">🚀</div>
        <p>Hit the button above to pull the latest news<br>
        tailored to your topics and publishers.</p>
    </div>
    """, unsafe_allow_html=True)
