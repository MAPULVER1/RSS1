
import feedparser
import streamlit as st
import pandas as pd
from datetime import datetime

def rss_scholar_tab(username):
    st.markdown("### 📡 Pull a Live Article to Log")
    rss_sources = {
            "NPR": "https://www.npr.org/rss/rss.php?id=1001",
            "Reuters": "http://feeds.reuters.com/reuters/topNews",
            "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
            "CNN": "http://rss.cnn.com/rss/edition.rss",
            "The Guardian": "https://www.theguardian.com/world/rss",
            "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
            "Fox News": "http://feeds.foxnews.com/foxnews/latest",
            "Bloomberg": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
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

    selected_source = st.selectbox("Choose a Source", list(rss_sources.keys()))
    feed = feedparser.parse(rss_sources[selected_source])
    headlines = [{ "title": entry.title, "link": entry.link } for entry in feed.entries[:10]]

    headline_map = { h["title"]: h["link"] for h in headlines }
    selected_title = st.selectbox("Choose a Headline", list(headline_map.keys()))

    if selected_title:
        selected_link = headline_map[selected_title]
        st.markdown(f"🔗 **[Preview Article]({selected_link})**")
        notes = st.text_area("Add your notes / reasoning below:", key="rss_notes")
        if st.button("Submit This Log", key="submit_rss_log"):
            auto_score = 1 + (2 if len(notes) >= 100 else 0)
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            log_entry = {
                "user": username,
                "title": selected_title,
                "link": selected_link,
                "notes": notes,
                "timestamp": now,
                "points_awarded": auto_score,
                "admin_notes": ""
            }
            try:
                df = pd.read_csv("scholar_logs.csv")
            except:
                df = pd.DataFrame(columns=list(log_entry.keys()))
            df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)
            df.to_csv("scholar_logs.csv", index=False)
            st.success("RSS log submitted successfully!")
