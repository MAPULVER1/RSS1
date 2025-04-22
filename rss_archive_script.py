import feedparser
import pandas as pd
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse
from dateutil import parser as dateparser
from safe_git_auto_push import safe_git_auto_push
from git_utils import safe_git_commit

safe_git_commit("🔄 Auto log update from RSS")
# This script fetches RSS feeds from various news sources, extracts article titles, and stores them in a CSV file.
# It also tags the articles with subjects and freshness ratings.


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
    "The Executive Branch": [
        "administration", "cabinet", "executive branch", "executive order", "federal agency", 
        "oval office", "president", "press secretary", "white house"
    ],
    "The Legislative Branch": [
        "bill", "bipartisan", "committee", "congress", "house of representatives", 
        "lawmakers", "legislation", "legislative session", "senate"
    ],
    "The Judicial Branch": [
        "appeals court", "indictment", "judicial", "jurisdiction", "justice", 
        "lawsuit", "legal review", "litigation", "precedent", "prosecution", 
        "ruling", "supreme court", "verdict"
    ],
    "Education": [
        "academic", "college", "curriculum", "education", "exam", "learning", 
        "school", "standardized test", "students", "teacher", "teaching", "university"
    ],
    "Technology": [
        "technology", "tech", "AI", "artificial intelligence", "robotics", 
        "data", "cybersecurity", "software", "hardware", "social media", 
        "algorithm", "computer", "internet"
    ],
    "Business & the Economy": [
        "inflation", "economy", "unemployment", "jobs", "recession", "market", 
        "federal reserve", "interest rate", "wage", "economic", "stimulus", "GDP", "monetary policy"
    ],
    "World Leaders": [
        "prime minister", "president", "diplomatic", "summit", "leader", 
        "government", "foreign policy", "chancellor", "ambassador", "head of state"
    ],
    "International Conflicts": [
        "war", "military", "conflict", "tensions", "invasion", "peace talks", 
        "allies", "bombing", "airstrike", "diplomatic dispute", "ceasefire", 
        "troops", "border clash", "missile", "nuclear", "occupation"
    ],
    "Business & Commerce": [
        "business", "corporate", "startup", "merger", "IPO", "stock market", 
        "commerce", "industry", "manufacturing", "retail", "supply chain"
    ],
    "The Global Economy": [
        "trade", "exports", "imports", "tariff", "global economy", 
        "world bank", "IMF", "G7", "G20", "economic development", "foreign exchange"
    ],
    "Human Rights": [
        "human rights", "civil rights", "freedom", "oppression", "refugee", 
        "genocide", "famine", "displacement", "inequality", "racism", 
        "protest", "prisoner", "asylum", "detention", "activist"
    ]
}

def tag_subject(title):
    title = title.lower()
    subject_scores = {}

    for subject, keywords in subject_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in title)
        if matches > 0:
            subject_scores[subject] = matches / len(keywords)

    if subject_scores:
        # Return the subject with the highest score
        return max(subject_scores, key=subject_scores.get)
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

for source, feed_url in rss_feeds.items():
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:10]:
        title = entry.title.strip()

    # Skip clickbait or media-junk headlines
    if any(prefix in title.upper() for prefix in ["LIVE:", "WATCH:", "WWE", "VIDEO:", "PHOTOS:", "GALLERY:"]):
        continue

    domain = urlparse(entry.link).netloc.replace("www.", "")
    if any(excl in domain for excl in excluded_domains):
        continue

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

# Convert the collected rows into a DataFrame
df_today = pd.DataFrame(rows)

# Define the archive file name
archive_file = "rss_archive.csv"

# Check if the archive file exists
if os.path.exists(archive_file):
    # Load the existing archive
    df_archive = pd.read_csv(archive_file)
    
    # Combine today's data with the archive, removing duplicates
    df_all = pd.concat([df_archive, df_today]).drop_duplicates(subset=["Date", "Title", "Link"])
else:
    # If no archive exists, use today's data as the starting point
    df_all = df_today

# Save the updated archive back to the file
df_all.to_csv(archive_file, index=False)

# Push changes to the repository if there are updates
if not df_today.empty:
    safe_git_auto_push()
    print(f"✅ Archived {len(df_today)} new headlines on {today}.")
else:
    print("ℹ️ No new headlines to archive today.")

