
import streamlit as st
st.set_page_config(page_title="PulverLogic RSS", layout="wide")

import pandas as pd
import feedparser
from datetime import datetime
from urllib.parse import urlparse
import os
from user_access import login, logout, route_user

# -----------------------
# SESSION STATE SETUP
# -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = "public"
if "impersonating" not in st.session_state:
    st.session_state.impersonating = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False

# -----------------------
# STATUS BAR
# -----------------------
def status_bar():
    if st.session_state.logged_in:
        user = st.session_state.username
        role = st.session_state.role
        icon = "🧑‍💼" if role == "admin" else "🎓" if role == "student" else "🔐"
        st.info(f"{icon} Logged in as: {user} ({role.title()})")
    else:
        st.warning("🔓 Public Mode — You are not logged in")

status_bar()

# -----------------------
# RSS FEED PARSING + ARCHIVING
# -----------------------
excluded_domains = ["economist.com", "ft.com", "nytimes.com", "wsj.com", "bloomberg.com"]

rss_feeds = {
    "NPR": "https://www.npr.org/rss/rss.php?id=1001",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Fox News": "http://feeds.foxnews.com/foxnews/latest",
    "The Washington Post": "http://feeds.washingtonpost.com/rss/national",
    "ABC News": "https://abcnews.go.com/abcnews/topstories",
    "CBS News": "https://www.cbsnews.com/latest/rss/main",
    "NBC News": "http://feeds.nbcnews.com/nbcnews/public/news",
    "USA Today": "http://rssfeeds.usatoday.com/usatoday-NewsTopStories",
    "Politico": "https://www.politico.com/rss/politics08.xml",
    "The Hill": "https://thehill.com/rss/syndicator/19110",
    "Time": "http://feeds2.feedburner.com/time/topstories",
    "Newsweek": "https://www.newsweek.com/rss",
    "The Atlantic": "https://www.theatlantic.com/feed/all/",
    "Sky News": "https://feeds.skynews.com/feeds/rss/home.xml",
    "Axios": "https://www.axios.com/rss"
}

def tag_subject(title):
    title = title.lower()
    subject_keywords = {
        "The Executive Branch": ["federal agency", "president", "white house", "potus", "constitution"],
        "The Legislative Branch": ["legislation", "committee hearing", "lawmaking", "senate"],
        "The Judicial Branch": ["judicial review", "due process", "prima facie", "precedent", "legal review"],
        "Education": ["pedagogy", "curriculum", "standardized testing"],
        "Technology": ["innovation", "ai", "hardware", "data privacy"],
        "Business & the Economy": ["inflation", "monetary policy", "gdp", "bonds"],
        "World Leaders": ["diplomacy", "sanctions", "geopolitical", "multilateralism"],
        "International Conflicts": ["proxy war", "military", "public opinion", "trade war"],
        "Business & Commerce": ["corporate", "startup", "assets", "speculation"],
        "The Global Economy": ["trade agreement", "exchange rate", "exports", "free trade"],
        "Human Rights": ["civil liberties", "humanitarian", "famine", "genocide"]
    }
    for subject, keywords in subject_keywords.items():
        if any(k in title for k in keywords):
            return subject
    return "General"

# -----------------------
# BUILD DAILY ARCHIVE
# -----------------------
today_str = datetime.today().strftime("%Y-%m-%d")
rows = []
for source, url in rss_feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:10]:
        domain = urlparse(entry.link).netloc.replace("www.", "")
        if any(excl in domain for excl in excluded_domains):
            continue
        rows.append({
            "Date": today_str,
            "Source": source,
            "Title": entry.title,
            "Link": entry.link,
            "Subject": tag_subject(entry.title)
        })

df_today = pd.DataFrame(rows)
archive_file = "rss_archive.csv"
if os.path.exists(archive_file):
    df_archive = pd.read_csv(archive_file)
    df_archive = pd.concat([df_archive, df_today]).drop_duplicates(subset=["Title"])
else:
    df_archive = df_today
df_archive.to_csv(archive_file, index=False)

# -----------------------
# ROUTE LOGIC
# -----------------------
if st.session_state.logged_in:
    route_user()
else:
    # Public homepage view
    st.title("🗞️ PulverLogic RSS - Public Dashboard")
    st.markdown("Welcome to the public view. Here you can see live headlines and archived visualizations.")

    if st.button("🔐 Scholar/Admin Login"):
        st.session_state.show_login = True

    if st.session_state.show_login:
        login()

    try:
        df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
        df_today = df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == today_str]
        st.subheader("📍 Today’s Headlines (Public Sample)")
        st.dataframe(df_today[["Date", "Title", "Source", "Subject"]].head(10))
    except:
        st.info("No public archive found.")
