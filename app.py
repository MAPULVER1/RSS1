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

# Try to load spaCy model, download if missing
def get_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        try:
            import spacy.cli  # type: ignore
            spacy.cli.download("en_core_web_sm")
            return spacy.load("en_core_web_sm")
        except Exception as e:
            st.error("spaCy model 'en_core_web_sm' is not installed and could not be downloaded automatically. Please run './setup.sh' or 'python3 -m spacy download en_core_web_sm' in your environment.")
            st.stop()
    # Ensure a return value even if st.stop() does not halt execution (for static analysis)
    return None

nlp = get_spacy_model()
if nlp is None:
    st.stop()

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
    df_archive = pd.DataFrame(columns=["Date", "Source", "Title", "Link"])  # Removed Subject

# -----------------------
# RSS PARSER FUNCTION
# -----------------------
def fetch_live_rss(feed_url):
    feed = feedparser.parse(feed_url)
    entries = []
    for entry in feed.entries[:10]:  # Limit to 10 new headlines per pull
        entries.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Source": feed.feed.get("title", "Unknown Source"),
            "Title": entry.get("title", "No title"),
            "Link": entry.get("link", "No link")
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
# ADVANCED QUESTION GENERATOR (spaCy)
# -----------------------
def to_question(headline):
    doc = nlp(headline)
    subj = next((tok.text for tok in doc if tok.dep_ == "nsubj"), None)
    verb = next((tok.lemma_ for tok in doc if tok.dep_ == "ROOT"), None)
    obj  = next((tok.text for tok in doc if tok.dep_ == "dobj"), None)
    if subj and verb and obj:
        templates = [
            f"What is the significance of {subj} {verb} {obj}?",
            f"How has {subj} {verb} {obj} affected society?",
            f"Should {subj} {verb} {obj}? Why or why not?"
        ]
        return random.choice(templates)
    return None

def generate_topics(headlines):
    questions = [q for h in headlines if (q := to_question(h))]
    return random.sample(questions, min(3, len(questions)))

# -----------------------
# ARTICLE RETRIEVAL (CACHED)
# -----------------------
@st.cache_data(max_entries=100)
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
    keywords = [tok.lemma_.lower() for tok in doc if tok.is_alpha and not tok.is_stop]
    mask = df["Title"].str.lower().apply(lambda t: any(k in t for k in keywords))
    articles = df[mask][["Title", "Link"]].drop_duplicates().head(10)
    articles = articles.to_dict(orient="records")
    for art in articles:
        art["text"] = fetch_article_text(art["Link"])
    return articles

# -----------------------
# LOGGING (topic + article titles)
# -----------------------
def log_selection(topic, articles):
    log_file = "topic_logs.csv"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "articles": "; ".join(a["Title"] for a in articles)
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
        df_archive = pd.concat([df_archive, st.session_state["live_rss"]]).drop_duplicates(subset=["Date", "Title", "Link"], keep="last").reset_index(drop=True)
        df_archive.to_csv(archive_file, index=False)
        safe_git_auto_push()
        st.success("Feed saved to archive and changes pushed to Git!")

# Show and auto-sort today's archive headlines
if not df_archive.empty:
    df_today = df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == today_str]
    df_today = df_today.sort_values(by=["Source", "Title"], ascending=True)
    st.subheader("📍 Today’s Headlines")
    st.dataframe(df_today[["Date", "Title", "Source"]])  # Removed Subject
    # Topic generation UI
    if st.button("Generate Topics"):
        st.session_state["topics"] = generate_topics(df_today["Title"])
    if st.session_state.get("topics"):
        choice = st.radio("Choose a topic:", st.session_state["topics"])
        if choice and st.button("Show Related Articles"):
            related = find_related_articles(choice, df_archive)
            for art in related:
                with st.expander(art["Title"]):
                    st.write(art["text"])
            log_selection(choice, related)
            st.success("Session logged.")
else:
    st.info("No public archive found.")


