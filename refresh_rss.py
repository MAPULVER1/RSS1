import feedparser
import pandas as pd
from datetime import datetime
import os
from urllib.parse import urlparse
from safe_git_auto_push import safe_git_auto_push


# RSS Feeds - Same as in archive script
rss_feeds = {
    "NPR": "https://www.npr.org/rss/rss.php?id=1001",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Fox News": "http://feeds.foxnews.com/foxnews/latest",
    "Bloomberg": "https://www.bloomberg.com/feeds/bbiz.xml",
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

# Excluded (paywalled or gated) domains
# Domains to exclude from RSS processing due to paywalls or restrictions
excluded_domains = ["economist.com", "ft.com", "nytimes.com"]

# Subject classification
subject_keywords = {
    "The Executive Branch": ["federal agency", "department", "president", "potus", "constitution"],
    "The Legislative Branch": ["legislation", "committee hearing", "lawmaking", "senate"],
    "The Judicial Branch": ["judicial review", "due process", "prima facie", "precedent", "legal review", "briefing", "due diligence"],
    "Education": ["mathematics", "science", "engineering", "pedagogy", "curriculum", "standardized testing"],
    "Technology": ["innovation", "ai", "hardware", "software", "algorithm", "data privacy"],
    "Business & the Economy": ["inflation", "gdp", "monetary policy", "wall street", "main street", "bonds"],
    "World Leaders": ["sanctions", "foreign diplomacy", "geopolitical", "multilateralism", "trade talks"],
    "International Conflicts": ["proxy war", "trade war", "negotiations", "public opinion", "military"],
    "Business & Commerce": ["corporate governance", "supply chain", "speculation", "assets"],
    "The Global Economy": ["trade agreement", "import", "export", "exchange rate", "free trade", "protectionism"],
    "Human Rights": ["civil liberties", "oppression", "censorship", "humanitarian", "food supply", "famine", "genocide"]
}

def tag_subject(title):
    title = title.lower()
    for subject, keywords in subject_keywords.items():
        if any(keyword in title for keyword in keywords):
            return subject
    return "General"

# Main function to refresh RSS archive
def refresh_rss():
    today = datetime.today().strftime("%Y-%m-%d")
    rows = []

    for source, url in rss_feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            domain = urlparse(entry.link).netloc.replace("www.", "")
            if any(bad in domain for bad in excluded_domains):
                continue
            rows.append({
                "Date": today,
                "Source": source,
                "Title": entry.title,
                "Link": entry.link,
                "Subject": tag_subject(entry.title)
            })

    new_df = pd.DataFrame(rows)
    archive_file = "rss_archive.csv"
    if os.path.exists(archive_file):
        df_archive = pd.read_csv(archive_file)
        df_all = pd.concat([df_archive, new_df]).drop_duplicates(subset=["Title", "Date"])
    else:
        df_all = new_df

    df_all.to_csv(archive_file, index=False)
    safe_git_auto_push()
    return len(new_df)

# Run the refresh (useful if called manually)
if __name__ == "__main__":
    count = refresh_rss()
    print(f"✅ Archived {count} new headlines.")
