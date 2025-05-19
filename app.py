import streamlit as st
st.set_page_config(page_title="Extemp Topic Generator", layout="wide")

import pandas as pd
import feedparser
from datetime import datetime
import os
import subprocess
import random
import spacy
from newspaper import Article

nlp = spacy.load("en_core_web_sm")

# -----------------------
# LOAD EXISTING ARCHIVE
# -----------------------
archive_file = "rss_archive.csv"
today_str = datetime.today().strftime("%Y-%m-%d")

try:
    df_archive = pd.read_csv(archive_file)
    df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
except Exception as e:
    st.error(f"⚠️ Failed to load RSS archive: {e}")
    df_archive = pd.DataFrame(columns=["Date", "Source", "Title", "Link", "Subject"])

# -----------------------
# RSS PARSER FUNCTION
# -----------------------
def fetch_live_rss(feed_url):
    feed = feedparser.parse(feed_url)
    entries = []
    for entry in feed.entries:
        entries.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Source": feed.feed.get("title", "Unknown Source"),
            "Title": entry.get("title", "No title"),
            "Link": entry.get("link", "No link"),
            "Subject": "General"
        })
    return pd.DataFrame(entries)

# -----------------------
# GIT AUTO PUSH FUNCTION
# -----------------------
def safe_git_auto_push():
    try:
        subprocess.run(["git", "config", "user.name", "MAPULVER1"], check=True)
        subprocess.run(["git", "config", "user.email", "michaelalexanderpulver@outlook.com"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-commit: Updated RSS archive"], check=True)
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Git operation failed: {e}")

# -----------------------
# NLTK-BASED QUESTION GENERATOR
# -----------------------
def to_question(headline):
    doc = nlp(headline)
    subj = next((tok.text for tok in doc if tok.dep_ == "nsubj"), None)
    verb = next((tok.lemma_ for tok in doc if tok.dep_ == "ROOT"), None)
    obj = next((tok.text for tok in doc if tok.dep_ == "dobj"), None)
    if subj and verb and obj:
        if random.choice(["informative", "persuasive"]) == "informative":
            return f"What has {subj} {verb} {obj}?"
        else:
            return f"Should {subj} {verb} {obj}?"
    return None

def generate_topics(headlines):
    questions = []
    for h in headlines:
        q = to_question(h)
        if q:
            questions.append(q)
    return random.sample(questions, min(3, len(questions)))

# -----------------------
# ARTICLE RETRIEVAL
# -----------------------
def fetch_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return "[Content not available]"

def find_related_articles(topic, df):
    doc = nlp(topic)
    keywords = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]
    mask = df["Title"].apply(lambda t: any(k in t.lower() for k in keywords))
    articles = df[mask][["Title", "Link"]].drop_duplicates().to_dict(orient="records")
    for art in articles:
        art["text"] = fetch_article_text(art["Link"])
    return articles

# -----------------------
# LOGGING
# -----------------------
def log_selection(topic, articles):
    log_file = "topic_logs.csv"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "articles": "; ".join(a["Link"] for a in articles)
    }
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
    else:
        df = pd.DataFrame(columns=["timestamp","topic","articles"])
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(log_file, index=False)
    safe_git_auto_push()

# -----------------------
# STREAMLIT UI
# -----------------------
st.title("🗞️ Extemp Topic Generator")

st.sidebar.header("🔄 Live RSS Fetch")
feed_url = st.sidebar.text_input(
    "RSS Feed URL",
    value="https://feeds.feedburner.com/TechCrunch/",
    help="Enter the URL of the RSS feed you want to fetch."
)
if st.sidebar.button("📅 Fetch Feed"):
    if feed_url.strip():
        df_live = fetch_live_rss(feed_url)
        st.session_state["live_rss"] = df_live
        st.success(f"Successfully fetched feed from: {feed_url}")
    else:
        st.error("Please provide a valid RSS feed URL.")

# Show live RSS results
if "live_rss" in st.session_state:
    st.subheader("🔞 Live RSS Feed Preview")
    st.dataframe(st.session_state["live_rss"])
    if st.button("📂 Save to Archive"):
        df_archive = pd.concat([df_archive, st.session_state["live_rss"]]).drop_duplicates(subset=["Link"], keep="last").reset_index(drop=True)
        df_archive.to_csv(archive_file, index=False)
        safe_git_auto_push()
        st.success("Feed saved to archive and changes pushed to Git!")

# Show and auto-sort today's archive headlines
if not df_archive.empty:
    df_today = df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == today_str]
    df_today = df_today.sort_values(by=["Source", "Title"], ascending=True)
    st.subheader("📍 Today’s Headlines")
    st.dataframe(df_today[["Date", "Title", "Source", "Subject"]])
    # Topic generation UI
    if st.button("Generate Topics"):
        st.session_state["topics"] = generate_topics(df_today["Title"].tolist())
    if st.session_state.get("topics"):
        choice = st.radio("Choose a topic:", st.session_state["topics"])
        if choice and st.button("Show Related Articles"):
            related = find_related_articles(choice, df_archive)
            for art in related[:10]:
                with st.expander(art["Title"]):
                    st.write(art["text"])
            log_selection(choice, related)
            st.success("Session logged.")
else:
    st.info("No public archive found.")


