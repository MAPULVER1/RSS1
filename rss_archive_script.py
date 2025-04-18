import feedparser
import pandas as pd
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse
from dateutil import parser as dateparser

# Skip known paywalled or unreliable domains
excluded_domains = [
    "economist.com", "ft.com", "nytimes.com", "wsj.com", "bloomberg.com"
]

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

subject_keywords = {
    "The Executive Branch": ["federal agency", "department", "president", "POTUS", "constitution"],
    "The Legislative Branch": ["legislation", "committee hearing", "lawmaking", "senate"],
    "The Judicial Branch": ["judicial review", "due process", "prima facie", "precedent", "legal review", "briefing", "due diligence"],
    "Education": ["mathematics", "science", "engineering", "pedagogy", "curriculum", "standardized testing"],
    "Technology": ["innovation", "AI", "hardware", "software", "algorithm", "data privacy"],
    "Business & the Economy": ["inflation", "GDP", "monetary policy", "wall street", "main street", "bonds"],
    "World Leaders": ["sanctions", "foreign diplomacy", "geopolitical", "multilateralism", "trade talks"],
    "International Conflicts": ["proxy war", "trade war", "negotiations", "public opinion", "military"],
    "Business & Commerce": ["corporate governance", "supply chain", "speculation", "assets"],
    "The Global Economy": ["trade agreement", "import", "export", "exchange rate", "free trade", "protectionism"],
    "Human Rights": ["civil liberties", "oppression", "censorship", "humanitarian", "food supply", "famine", "genocide"]
}

def tag_subject(title):
    title = title.lower()
    for subject, keywords in subject_keywords.items():
        if any(k.lower() in title for k in keywords):
            return subject
    return "General"

def subject_confidence(title, subject):
    title = title.lower()
    keywords = subject_keywords.get(subject, [])
    matches = sum(1 for word in keywords if word.lower() in title)
    return round(matches / len(keywords), 2) if keywords else 0.0

def tag_freshness(pub_date_str):
    try:
        pub_date = dateparser.parse(pub_date_str)
        now = datetime.utcnow()
        if (now - pub_date) < timedelta(hours=3):
            return "Top of News"
    except:
        pass
    return "In the News"

today = datetime.today().strftime("%Y-%m-%d")
rows = []

for source, url in rss_feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:10]:
        domain = urlparse(entry.link).netloc.replace("www.", "")
        if any(excl in domain for excl in excluded_domains):
            continue

        title = entry.title
        subject = tag_subject(title)
        confidence = subject_confidence(title, subject)
        freshness = tag_freshness(entry.get("published", ""))

        rows.append({
            "Date": today,
            "Source": source,
            "Title": title,
            "Link": entry.link,
            "Subject": subject,
            "Subject Confidence": confidence,
            "Story Type": freshness
        })

df_today = pd.DataFrame(rows)

archive_file = "rss_archive.csv"
if os.path.exists(archive_file):
    df_archive = pd.read_csv(archive_file)
    df_all = pd.concat([df_archive, df_today]).drop_duplicates(subset=["Date", "Title", "Link"])
else:
    df_all = df_today

df_all.to_csv(archive_file, index=False)
print(f"✅ Archived {len(df_today)} new headlines on {today}.")

