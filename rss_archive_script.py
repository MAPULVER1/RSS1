import feedparser
import pandas as pd
from datetime import datetime
import os
from urllib.parse import urlparse

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

def refresh_rss_archive():
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
                "Link": entry.link
            })
    new_df = pd.DataFrame(rows)
    archive_file = "rss_archive.csv"
    if os.path.exists(archive_file):
        df_archive = pd.read_csv(archive_file)
        df_all = pd.concat([df_archive, new_df]).drop_duplicates(subset=["Date", "Title", "Link"])
    else:
        df_all = new_df
    df_all.to_csv(archive_file, index=False)
    return len(new_df)

if __name__ == "__main__":
    count = refresh_rss_archive()
    print(f"✅ Archived {count} new headlines.")

