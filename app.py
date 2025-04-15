
import streamlit as st
import feedparser
import pandas as pd

# Initialize Streamlit app
st.set_page_config(page_title="Enhanced Newsboard", layout="wide")
st.title("🗞️ Enhanced RSS Newsboard")

# Define RSS feeds
rss_urls = {
    "NPR Education": "https://www.npr.org/rss/rss.php?id=1014",
    "Al Jazeera Top": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters World": "http://feeds.reuters.com/reuters/worldNews",
}

# Placeholder for bias and credibility
bias_credibility_map = {
    "NPR Education": {"Bias": "Left", "Credibility": "High"},
    "Al Jazeera Top": {"Bias": "Center", "Credibility": "High"},
    "Reuters World": {"Bias": "Center", "Credibility": "High"},
}

# Placeholder for thematic filters
thematic_keywords = {
    "Education": ["school", "student", "university", "teacher"],
    "Technology": ["tech", "AI", "data", "software"],
    "Politics": ["election", "policy", "congress", "government"],
}

all_articles = []

# Fetch articles
for source, url in rss_urls.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]:
        # Determine the theme based on keywords in the title
        theme = next(
            (theme_name for theme_name, keywords in thematic_keywords.items()
             if any(keyword.lower() in entry.title.lower() for keyword in keywords)),
            "General"
        )
        # Add articles with bias, credibility, and theme
        all_articles.append({
            "Source": source,
            "Title": entry.title,
            "Link": entry.link,
            "Published": entry.published if 'published' in entry else "N/A",
            "Bias": bias_credibility_map[source]["Bias"],
            "Credibility": bias_credibility_map[source]["Credibility"],
            "Theme": theme
        })

# Convert to DataFrame
df = pd.DataFrame(all_articles)

# Sidebar: Thematic Filters
selected_theme = st.sidebar.selectbox("Filter by Theme", ["All", "Education", "Technology", "Politics"])
if selected_theme != "All":
    df = df[df["Theme"] == selected_theme]

# Display filtered DataFrame
st.dataframe(df)

# Expandable article list
st.subheader("📚 Article Details")
for index, row in df.iterrows():
    with st.expander(row["Title"]):
        st.write(f"**Source:** {row['Source']} | Published: {row['Published']}")
        st.write(f"**Bias:** {row['Bias']} | **Credibility:** {row['Credibility']}")
        st.markdown(f"[Read Full Article]({row['Link']})")
        st.markdown("---")

# Debate Mode: Show opposing viewpoints
st.subheader("🤔 Debate Mode: Compare Perspectives")
left_articles = df[df["Bias"] == "Left"].head(3)
center_articles = df[df["Bias"] == "Center"].head(3)
right_articles = df[df["Bias"] == "Right"].head(3)

st.markdown("**Left-leaning Articles:**")
for _, row in left_articles.iterrows():
    st.write(f"- {row['Title']} ([Read more]({row['Link']}))")

st.markdown("**Center Articles:**")
for _, row in center_articles.iterrows():
    st.write(f"- {row['Title']} ([Read more]({row['Link']}))")

st.markdown("**Right-leaning Articles:**")
for _, row in right_articles.iterrows():
    st.write(f"- {row['Title']} ([Read more]({row['Link']}))")
