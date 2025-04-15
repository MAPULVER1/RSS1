
import streamlit as st
import feedparser
import pandas as pd
import openai
import os

# Set page configuration
st.set_page_config(page_title="Smart RSS Dashboard", layout="wide")
st.title("🗞️ Smart RSS Newsboard with GPT Summaries")

# Load OpenAI API key securely from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Define RSS feeds
rss_urls = {
    "NPR Education": "https://www.npr.org/rss/rss.php?id=1014",
    "Al Jazeera Top": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters World": "http://feeds.reuters.com/reuters/worldNews",
}

# Bias and credibility mapping
bias_credibility_map = {
    "NPR Education": {"Bias": "Left", "Credibility": "High"},
    "Al Jazeera Top": {"Bias": "Center", "Credibility": "High"},
    "Reuters World": {"Bias": "Center", "Credibility": "High"},
}

# Thematic keyword mapping
thematic_keywords = {
    "Education": ["school", "student", "university", "teacher"],
    "Technology": ["tech", "AI", "data", "software"],
    "Politics": ["election", "policy", "congress", "government"],
}

# Summarization function with caching
@st.cache_data(show_spinner=False)
def generate_summary(title, source, theme):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful news summarizer."},
                {"role": "user", "content": f"Summarize this news title in 1–2 sentences:\n\n'{title}'\n\nIt is from {source} and relates to {theme}."}
            ],
            max_tokens=60,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Summary unavailable: {str(e)}"

# Collect all articles
all_articles = []

for source, url in rss_urls.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]:
        title = entry.title
        theme = next(
            (t for t, keywords in thematic_keywords.items()
             if any(k.lower() in title.lower() for k in keywords)),
            "General"
        )
        summary = generate_summary(title, source, theme)
        all_articles.append({
            "Source": source,
            "Title": title,
            "Link": entry.link,
            "Published": entry.published if 'published' in entry else "N/A",
            "Bias": bias_credibility_map[source]["Bias"],
            "Credibility": bias_credibility_map[source]["Credibility"],
            "Theme": theme,
            "Summary": summary
        })

# Convert to DataFrame
df = pd.DataFrame(all_articles)

# Sidebar filter
selected_theme = st.sidebar.selectbox("Filter by Theme", ["All", "Education", "Technology", "Politics", "General"])
if selected_theme != "All":
    df = df[df["Theme"] == selected_theme]

# Display articles
st.dataframe(df[["Source", "Title", "Published", "Bias", "Credibility", "Theme"]])

# Expandable article cards
st.subheader("📚 Article Summaries")
for index, row in df.iterrows():
    with st.expander(row["Title"]):
        st.write(f"**Source:** {row['Source']} | Published: {row['Published']}")
        st.write(f"**Bias:** {row['Bias']} | **Credibility:** {row['Credibility']}")
        st.write(f"**Theme:** {row['Theme']}")
        st.write(f"**Summary:** {row['Summary']}")
        st.markdown(f"[Read Full Article]({row['Link']})")
        st.markdown("---")

# Debate Mode
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
