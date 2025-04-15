
import streamlit as st
import feedparser
import pandas as pd

st.set_page_config(page_title="Live Newsboard", layout="wide")
st.title("🗞️ Live Newsboard")

# Define RSS feeds
rss_urls = {
    "NPR Education": "https://www.npr.org/rss/rss.php?id=1014",
    "Al Jazeera Top": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters World": "http://feeds.reuters.com/reuters/worldNews",
}

# Collect and parse RSS feeds
all_articles = []
for name, url in rss_urls.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]:
        all_articles.append({
            "Source": name,
            "Title": entry.title,
            "Link": entry.link,
            "Published": entry.published if 'published' in entry else "N/A"
        })

# Convert to DataFrame
df = pd.DataFrame(all_articles)

# Display DataFrame
st.dataframe(df)

# Expandable detailed list
st.subheader("📚 Article Summaries")
for index, row in df.iterrows():
    with st.expander(row['Title']):
        st.write(f"**Source:** {row['Source']} | Published: {row['Published']}")
        st.markdown(f"[Read Full Article]({row['Link']})")
        st.markdown("---")
