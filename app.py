import os
import streamlit as st # type: ignore
st.set_page_config(page_title="Extemp Topic Generator", layout="wide")

import spacy
nlp = spacy.load("./en_core_web_sm")

import pandas as pd
import feedparser # type: ignore
from datetime import datetime, timedelta
import subprocess
import random
from newspaper import Article # type: ignore
import csv

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

# --- SIDEBAR: RSS Feed Selection ---
rss_list_file = "rss_feeds.csv"
def get_rss_feeds():
    feeds = []
    if os.path.exists(rss_list_file):
        with open(rss_list_file, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                feeds.append(row)
    return feeds

rss_feeds = get_rss_feeds()
feed_names = [f["Name"] for f in rss_feeds] if rss_feeds else []
feed_urls = {f["Name"]: f["URL"] for f in rss_feeds} if rss_feeds else {}

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
    # Ensure input is a string
    if not isinstance(headline, str) or not headline.strip():
        return None
    doc = nlp(headline)
    # Try SVO
    subj = next((tok.text for tok in doc if tok.dep_ == "nsubj"), None)
    verb = next((tok.lemma_ for tok in doc if tok.dep_ == "ROOT"), None)
    obj  = next((tok.text for tok in doc if tok.dep_ == "dobj"), None)
    if subj and verb and obj:
        templates = [
            f"What is the significance of {subj} {verb} {obj}?",
            f"How has {subj} {verb} {obj} affected society?",
            f"Should {subj} {verb} {obj}? Why or why not?"
        ]
        # Return all templates for more variety
        return [t for t in templates]
    # Try NER-based
    ents = [ent for ent in doc.ents if ent.label_ in ("PERSON", "ORG", "GPE", "EVENT", "LAW", "LOC")]
    if ents and verb:
        ent = ents[0].text
        templates = [
            f"What is the impact of {ent} {verb}?",
            f"How is {ent} involved in current events?",
            f"What challenges does {ent} face regarding {verb}?"
        ]
        return [t for t in templates]
    # Fallback: generic question
    if len(headline.split()) > 3:
        return [f"What are the implications of: '{headline}'?"]
    # Final fallback: rephrase as a yes/no question
    if len(headline.split()) > 1:
        return [f"Should we be concerned about: '{headline}'?"]
    return []

def generate_topics(headlines):
    valid_headlines = [str(h) for h in headlines if isinstance(h, str) and h.strip()]
    all_questions = []
    for h in valid_headlines:
        qs = to_question(h)
        if qs:
            all_questions.extend(qs)
    # Remove duplicates and keep order
    seen = set()
    unique_questions = []
    for q in all_questions:
        if q not in seen:
            unique_questions.append(q)
            seen.add(q)
    # Always provide at least 3 questions, even if generic
    while len(unique_questions) < 3 and valid_headlines:
        filler = f"What are the implications of: '{random.choice(valid_headlines)}'?"
        if filler not in unique_questions:
            unique_questions.append(filler)
    while len(unique_questions) < 3:
        unique_questions.append("What are the implications of current events?")
    return random.sample(unique_questions, min(3, len(unique_questions)))

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
# Prune archive to only keep last 30 days
# -----------------------
cutoff_date = datetime.today() - timedelta(days=30)
df_archive = df_archive[df_archive["Date"] >= cutoff_date]

# -----------------------
# STREAMLIT UI
# -----------------------
st.title("🗞️ Extemp Topic Generator")

# --- SIDEBAR: Static News Sites Only ---
st.sidebar.header("🌐 News Sites (Sources)")
news_sites = [
    ("BBC News", "https://www.bbc.com/news"),
    ("Reuters", "https://www.reuters.com/"),
    ("NPR", "https://www.npr.org/sections/news/"),
    ("Al Jazeera", "https://www.aljazeera.com/news/"),
    ("The Guardian", "https://www.theguardian.com/international"),
    ("TechCrunch", "https://techcrunch.com/"),
    ("AP News", "https://apnews.com/"),
    ("Politico", "https://www.politico.com/"),
    ("NY Times", "https://www.nytimes.com/section/world"),
    ("CNN", "https://www.cnn.com/world")
]
for name, url in news_sites:
    st.sidebar.markdown(f"- [{name}]({url})")

# --- MAIN: Top Headlines and Topic Generation ---
if not df_archive.empty:
    df_today = df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == today_str]
    df_today = df_today.sort_values(by=["Source", "Title"], ascending=True)
    st.subheader("📍 Top Headlines for Today")
    st.dataframe(df_today[["Date", "Title", "Source"]], use_container_width=True)
    st.write(f"Headlines available for topic generation: {len(df_today['Title'])}")
    # --- Step 1: Generate Topics Button ---
    if "topics" not in st.session_state or st.button("Generate 3 Extemp Topics"):
        questions = generate_topics(df_today["Title"])
        st.session_state["topics"] = questions
        st.session_state.pop("locked_topic", None)
        st.session_state.pop("justification", None)
    # --- Step 2: Student Chooses One Topic ---
    if st.session_state.get("topics"):
        st.subheader("🔎 Choose Your Extemp Topic")
        choice = st.radio("Select one of the following topics:", st.session_state["topics"])
        if st.button("Lock Topic Selection"):
            st.session_state["locked_topic"] = choice
            st.session_state["justification"] = ""
    # --- Step 3: Justification and Research ---
    if st.session_state.get("locked_topic"):
        st.success(f"Topic locked: {st.session_state['locked_topic']}")
        st.write("### Research & Justify Your Topic Selection")
        related = find_related_articles(st.session_state["locked_topic"], df_archive)
        st.write("#### Relevant Research Articles:")
        if related:
            for art in related:
                st.markdown(f"**[{art['Title']}]({art['Link']})**")
                st.write(art["text"][:500] + ("..." if len(art["text"]) > 500 else ""))
        else:
            st.info("No related articles found in the archive.")
        st.write("#### Your Justification:")
        justification = st.text_area("Explain why this topic is feasible and interesting, using evidence from the articles above.", value=st.session_state.get("justification", ""))
        if st.button("Submit Justification"):
            st.session_state["justification"] = justification
            log_selection(st.session_state["locked_topic"], related)
            st.success("Topic and justification logged. Good luck!")
else:
    st.info("No public archive found.")


