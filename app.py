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
from streamlit_autorefresh import st_autorefresh

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

st.sidebar.header("🔄 Live RSS Fetch")
if feed_names:
    selected_feed = st.sidebar.selectbox("Choose an RSS Feed", feed_names)
    feed_url = feed_urls[selected_feed]
else:
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
        return random.choice(templates)
    # Try NER-based
    ents = [ent for ent in doc.ents if ent.label_ in ("PERSON", "ORG", "GPE", "EVENT", "LAW", "LOC")]
    if ents and verb:
        ent = ents[0].text
        templates = [
            f"What is the impact of {ent} {verb}?",
            f"How is {ent} involved in current events?",
            f"What challenges does {ent} face regarding {verb}?"
        ]
        return random.choice(templates)
    # Fallback: generic question
    if len(headline.split()) > 3:
        return f"What are the implications of: '{headline}'?"
    # Final fallback: rephrase as a yes/no question
    if len(headline.split()) > 1:
        return f"Should we be concerned about: '{headline}'?"
    return None

def generate_topics(headlines):
    # Filter out empty or non-string headlines
    valid_headlines = [str(h) for h in headlines if isinstance(h, str) and h.strip()]
    questions = [q for h in valid_headlines if (q := to_question(h))]
    # Always provide at least 3 questions, even if generic
    while len(questions) < 3 and valid_headlines:
        filler = f"What are the implications of: '{random.choice(valid_headlines)}'?"
        if filler not in questions:
            questions.append(filler)
    # If still not enough, add generic placeholders
    while len(questions) < 3:
        questions.append("What are the implications of current events?")
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
# Prune archive to only keep last 30 days
# -----------------------
cutoff_date = datetime.today() - timedelta(days=30)
df_archive = df_archive[df_archive["Date"] >= cutoff_date]

# -----------------------
# STREAMLIT UI
# -----------------------
st.title("🗞️ Extemp Topic Generator")

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
    st.dataframe(df_today[["Date", "Title", "Source"]])
    # Debug: Show number of headlines
    st.write(f"Headlines available for topic generation: {len(df_today['Title'])}")
    # Topic generation UI
    if st.button("Generate Topics"):
        questions = generate_topics(df_today["Title"])
        st.session_state["topics"] = questions
        # Debug: Show number of questions generated
        st.write(f"Questions generated: {len(questions)}")
        if not questions:
            st.warning("No extemp questions could be generated from today's headlines. Check your archive or question logic.")
    if st.session_state.get("topics"):
        if not st.session_state["topics"]:
            st.warning("No topics available. Try fetching new RSS headlines or check your archive.")
        else:
            st.subheader("🔎 Research & Select a Topic")
            for idx, topic in enumerate(st.session_state["topics"]):
                with st.expander(f"Topic {idx+1}: {topic}"):
                    st.write("#### Relevant Research Articles:")
                    related = find_related_articles(topic, df_archive)
                    if related:
                        for art in related:
                            st.markdown(f"**[{art['Title']}]({art['Link']})**")
                            st.write(art["text"][:500] + ("..." if len(art["text"]) > 500 else ""))
                    else:
                        st.info("No related articles found in the archive.")
                    if st.button(f"Select Topic {idx+1}"):
                        log_selection(topic, related)
                        st.success(f"Selected and logged: {topic}")
else:
    st.info("No public archive found.")

# --- RECOMMENDED QUESTIONS FOR UI/UX IMPROVEMENT ---
st.sidebar.markdown("---")
st.sidebar.header("💡 Extemp App Design Prompts")
st.sidebar.markdown("1. **How would you like to prepare for an extemporaneous speech? What would the display to work from look like?**\n2. **How can that page be functional and broad in its ability to be all-encompassing?**\n3. **What functions are being pulled from the repository that would not otherwise be a back-end need?**\n4. **Are questions supposed to be challenging? If so, do the questions follow a clear delineation between argument and rhetoric?**\n5. **With all errors, why are we not being direct about the true nature of the frontend landscape?**")


