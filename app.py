"""
My News Button 📰
Final Version with Onboarding + All Previous Features
"""

import time
import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import quote

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="My News Button", page_icon="📰", layout="wide")

# ====================== DEFAULT SETTINGS ======================
DEFAULT_PUBLISHERS = [
    "The Indian Express", "Hindustan Times", "The Hindu", "Economic Times"
]

ALL_TOPICS = [
    "AI", "Agentic AI", "Technology", "Renewable Energy", "Economy",
    "Indian Stock Market", "Fortune 500", "Startups", "Automobiles",
    "Cryptocurrency", "Politics", "Geopolitics", "Current Affairs",
    "Sports", "Business News"
]

# ====================== SESSION STATE ======================
if 'user_info_saved' not in st.session_state:
    st.session_state.user_info_saved = False

if 'username' not in st.session_state:
    st.session_state.username = ""

if 'email' not in st.session_state:
    st.session_state.email = ""

if 'custom_topics' not in st.session_state:
    st.session_state.custom_topics = []

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
    [data-testid="stAppViewContainer"], [data-testid="stMain"] { background-color: #F9F7F0 !important; }
    .main-title { text-align: center; font-family: 'Georgia', serif; font-size: 2.8rem; font-weight: 700; color: #1F1F1F; margin-bottom: 0.5rem; }
    .greeting { text-align: center; font-size: 1.25rem; color: #2C2C2C; margin-bottom: 2rem; }
    div[data-testid="stButton"] > button {
        background-color: #2C5F4A !important; color: white !important;
        font-size: 1.05rem !important; font-weight: 600 !important; padding: 0.7rem 2.5rem !important; border-radius: 10px !important;
    }
    .article-table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.07); }
    .article-table th { background-color: #F4F1E9; padding: 14px 12px; text-align: left; font-weight: 600; }
    .article-table td { padding: 14px 12px; border-bottom: 1px solid #EDE9DF; }
    .article-table a { color: #1F1F1F; text-decoration: none; font-weight: 500; }
    .article-table a:hover { color: #2C5F4A; text-decoration: underline; }
    .topic-header { background-color: #F4F1E9; padding: 12px 16px; border-radius: 8px; margin: 25px 0 12px 0; font-size: 1.2rem; font-weight: 600; color: #1F1F1F; }
    .custom-chip { 
        display: inline-block; background: #2C5F4A; color: white; padding: 6px 14px; 
        border-radius: 20px; margin: 5px 5px 5px 0; font-size: 0.92rem;
    }
</style>
""", unsafe_allow_html=True)

# ====================== ONBOARDING ======================
if not st.session_state.user_info_saved:
    st.markdown('<div class="main-title">My News Button 📰</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <h2>Welcome to My News Button</h2>
        <p>Please enter your details to personalize your experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Your Name", placeholder="Enter your name")
        email = st.text_input("Email Address", placeholder="your@email.com")
        
        if st.button("Save & Continue", use_container_width=True, type="primary"):
            if username.strip() and email.strip():
                st.session_state.username = username.strip()
                st.session_state.email = email.strip()
                st.session_state.user_info_saved = True
                st.success(f"Welcome, {username.strip()}! 🎉")
                st.rerun()
            else:
                st.error("Please fill both Name and Email")

else:
    # ====================== MAIN APP ======================
    st.markdown('<div class="main-title">My News Button 📰</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="greeting">Hi {st.session_state.username}, welcome again</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Select Topics")
        
        selected_predefined = []
        for topic in ALL_TOPICS:
            if st.checkbox(topic, value=False, key=f"chk_{topic}"):
                selected_predefined.append(topic)
        
        st.markdown("---")
        
        st.markdown("### ➕ Add Custom Topic")
        custom_input = st.text_input("Enter new topic", placeholder="e.g. EV Battery Technology", key="custom_input_key")
        
        col_add, col_clear = st.columns([3, 1])
        with col_add:
            if st.button("Add Topic", use_container_width=True):
                if custom_input.strip():
                    new_topic = custom_input.strip()
                    if new_topic not in st.session_state.custom_topics and new_topic not in selected_predefined:
                        st.session_state.custom_topics.append(new_topic)
                        st.success(f"Added: {new_topic}")
                    else:
                        st.warning("This topic already exists")
        
        with col_clear:
            if st.button("Clear Custom", use_container_width=True):
                st.session_state.custom_topics = []
                st.rerun()

        all_selected_topics = selected_predefined + st.session_state.custom_topics
        
        if all_selected_topics:
            st.markdown("**Selected Topics:**")
            for t in all_selected_topics:
                st.markdown(f'<span class="custom-chip">{t}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        max_articles = st.slider("Max articles per topic", 3, 12, 6)

    # Main Button
    _, col, _ = st.columns([1, 2, 1])
    with col:
        fetch_clicked = st.button("Fetch Latest News", use_container_width=True)

    if fetch_clicked:
        all_selected_topics = selected_predefined + st.session_state.custom_topics
        
        if not all_selected_topics:
            st.warning("⚠️ Please select at least one topic or add a custom topic.")
        else:
            progress_bar = st.progress(0, text="Fetching news for selected topics...")
            
            df = fetch_articles(all_selected_topics, DEFAULT_PUBLISHERS, max_articles)
            
            progress_bar.progress(100, text="Completed!")
            time.sleep(0.4)
            progress_bar.empty()

            if df.empty:
                st.warning("No recent articles found. Try different topics.")
            else:
                st.success(f"✅ Found {len(df)} recent articles")

                for topic, group in df.groupby("Topic"):
                    st.markdown(f'<div class="topic-header">📌 {topic} — {len(group)} articles</div>', unsafe_allow_html=True)
                    
                    html_table = """
                    <table class="article-table">
                        <thead><tr>
                            <th>Article Title</th>
                            <th>Publisher</th>
                            <th>Published</th>
                        </tr></thead>
                        <tbody>
                    """
                    for _, row in group.iterrows():
                        html_table += f"""
                            <tr>
                                <td><a href="{row['Link']}" target="_blank" rel="noopener noreferrer">{row['Title']}</a></td>
                                <td>{row['Publisher']}</td>
                                <td>{row['Published']}</td>
                            </tr>
                        """
                    html_table += "</tbody></table><br>"
                    st.html(html_table)

    else:
        st.info("Select topics or add custom ones, then click the button.")

st.caption("Recent articles (last 48 hours) • Grouped by selected topics")


# ====================== HELPER FUNCTIONS ======================
def build_rss_url(keyword: str, source_domain: str) -> str:
    query = f"site:{source_domain} {keyword}"
    encoded = quote(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"

def parse_published_time(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6])
        except:
            pass
    return None

def is_recent(pub_date, days=2):
    if not pub_date:
        return True
    cutoff = datetime.now() - timedelta(days=days)
    return pub_date >= cutoff

def fetch_articles(selected_topics, publishers, max_articles):
    articles = []
    seen = set()
    
    for pub in publishers:
        domain = PUBLISHER_SOURCE_MAP.get(pub)
        if not domain: continue
        for kw in selected_topics:
            url = build_rss_url(kw, domain)
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    title = getattr(entry, "title", "").strip()
                    if not title or title.lower() in seen: continue
                    seen.add(title.lower())
                    
                    pub_date = parse_published_time(entry)
                    if not is_recent(pub_date): continue
                    
                    articles.append({
                        "Topic": kw,
                        "Title": title,
                        "Link": getattr(entry, "link", "#"),
                        "Publisher": pub,
                        "Published": pub_date.strftime("%d %b %Y, %I:%M %p") if pub_date else "—",
                        "Published_dt": pub_date
                    })
            except:
                continue
    
    df = pd.DataFrame(articles)
    if not df.empty:
        df = df.sort_values(by=["Topic", "Published_dt"], ascending=[True, False])
        df = df.groupby("Topic").head(max_articles)
        df = df.drop(columns=["Published_dt"])
    return df

PUBLISHER_SOURCE_MAP = {
    "The Indian Express": "indianexpress.com",
    "Hindustan Times": "hindustantimes.com",
    "The Hindu": "thehindu.com",
    "Economic Times": "economictimes.indiatimes.com",
}
