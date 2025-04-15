
import feedparser, pandas as pd
from datetime import datetime
import os

rss_feeds = {
    "NPR": "https://www.npr.org/rss/rss.php?id=1001",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "The New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
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
    "The Economist": "https://www.economist.com/the-world-this-week/rss.xml",
    "Financial Times": "https://www.ft.com/?format=rss",
    "Sky News": "https://feeds.skynews.com/feeds/rss/home.xml",
    "Axios": "https://www.axios.com/rss"
}

def tag_subject(title):
    title = title.lower()
    subject_keywords = {
        "The Executive Branch": ["president", "white house", "executive", "biden"],
        "The Legislative Branch": ["congress", "senate", "house", "bill"],
        "The Judicial Branch": ["court", "judge", "justice", "ruling"],
        "Education": ["education", "school", "student", "teacher"],
        "Technology": ["ai", "tech", "data", "software"],
        "Business & the Economy": ["inflation", "market", "finance", "jobs"],
        "World Leaders": ["putin", "xi", "modi", "zelensky"],
        "International Conflicts": ["war", "missile", "invasion", "conflict"],
        "Business & Commerce": ["merger", "startup", "stock", "company"],
        "The Global Economy": ["global", "exports", "imports", "trade"],
        "Human Rights": ["rights", "freedom", "protest", "oppression"]
    }
    for subject, keywords in subject_keywords.items():
        if any(k in title for k in keywords):
            return subject
    return "General"

archive_file = "rss_archive.csv"
today = datetime.today().strftime("%Y-%m-%d")
rows = []

for source, url in rss_feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:10]:
        rows.append({
            "Date": today,
            "Source": source,
            "Title": entry.title,
            "Link": entry.link,
            "Subject": tag_subject(entry.title)
        })

df_today = pd.DataFrame(rows)

if os.path.exists(archive_file):
    df_archive = pd.read_csv(archive_file)
    df_all = pd.concat([df_archive, df_today]).drop_duplicates(subset=["Date", "Title"])
else:
    df_all = df_today

df_all.to_csv(archive_file, index=False)
print(f"Archived {len(df_today)} new headlines.")
