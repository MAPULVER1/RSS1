
import streamlit as st
import feedparser
import pandas as pd
import openai
from openai import OpenAI
import matplotlib.pyplot as plt
from collections import Counter
import re

# Set Streamlit page settings
st.set_page_config(page_title="Academic RSS Dashboard", layout="wide")
st.title("📚 Academic RSS Dashboard with Warrant Generation + Smart Visuals")

# Load API Key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Academic-style credibility tags by source
credibility_tags = {
    "NPR Education": "News Source (Credentialed, Independent)",
    "Al Jazeera Top": "News Source (Credentialed, Independent)",
    "Reuters World": "News Source (Credentialed, Independent)",
}

# RSS Feeds
rss_urls = {
    "NPR Education": "https://www.npr.org/rss/rss.php?id=1014",
    "Al Jazeera Top": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters World": "http://feeds.reuters.com/reuters/worldNews",
}

# Bias tags
bias_tags = {
    "NPR Education": "Left",
    "Al Jazeera Top": "Center",
    "Reuters World": "Center",
}

# Extract trending topics from headlines
def extract_trending_keywords(headlines, top_n=5):
    words = []
    for title in headlines:
        words += re.findall(r"\b\w+\b", title.lower())
    stopwords = set(["the", "of", "and", "in", "to", "on", "for", "with", "a", "is", "at", "as", "by", "an", "from", "this", "that", "it"])
    keywords = [w for w in words if w not in stopwords and len(w) > 3]
    return dict(Counter(keywords).most_common(top_n))

# Warrant generation function
def generate_warrant(title, source, theme, bias):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a debate coach. Given a news headline, identify a possible claim and warrant (reasoning) a student could use in a debate."},
                {"role": "user", "content": f"Headline: '{title}'\nTheme: {theme}\nBias: {bias}\nSource: {source}"}
            ],
            max_tokens=120,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Warrant unavailable: {str(e)}"

# Article list
all_articles = []

for source, url in rss_urls.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]:
        title = entry.title
        credibility = credibility_tags.get(source, "Unverified / Blog / Aggregator")
        bias = bias_tags.get(source, "Unspecified")
        all_articles.append({
            "Source": source,
            "Title": title,
            "Link": entry.link,
            "Published": entry.published if 'published' in entry else "N/A",
            "Bias": bias,
            "Credibility": credibility
        })

# Create DataFrame
df = pd.DataFrame(all_articles)

# Sidebar (optional filtering if expanded later)
st.sidebar.header("🔍 Filter (future)")

# Visuals
st.subheader("📊 News Snapshot Visuals")

col1, col2 = st.columns(2)

# Pie chart for credibility
with col1:
    st.markdown("### Credibility Distribution")
    credibility_counts = df["Credibility"].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(credibility_counts, labels=credibility_counts.index, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

# Bar chart for trending keywords
with col2:
    st.markdown("### Trending Keywords from Headlines")
    keyword_freq = extract_trending_keywords(df["Title"].tolist())
    fig2, ax2 = plt.subplots()
    ax2.bar(keyword_freq.keys(), keyword_freq.values())
    ax2.set_ylabel("Mentions")
    ax2.set_xlabel("Keyword")
    ax2.set_title("Top Terms in Current Headlines")
    st.pyplot(fig2)

# Data Table
st.subheader("🗂 Article Table")
st.dataframe(df[["Source", "Title", "Published", "Bias", "Credibility"]])

# Expandable Warrant Generator
st.subheader("🤔 Generate Argument Warrants")
for index, row in df.iterrows():
    with st.expander(row["Title"]):
        st.write(f"**Source:** {row['Source']} | Published: {row['Published']}")
        st.write(f"**Bias:** {row['Bias']} | **Credibility:** {row['Credibility']}")
        st.markdown(f"[Read Full Article]({row['Link']})")

        if st.button(f"🧠 Generate Warrant for: {row['Title']}", key=row['Title']):
            with st.spinner("Analyzing article..."):
                warrant = generate_warrant(row["Title"], row["Source"], "Unspecified", row["Bias"])
                st.success("Warrant Generated:")
                st.write(warrant)
