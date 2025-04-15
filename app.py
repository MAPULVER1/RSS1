
import streamlit as st
import feedparser
import pandas as pd
import openai
from openai import OpenAI
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="Warrant-Focused Newsboard", layout="wide")
st.title("🗞️ Smart RSS Newsboard with Warrant Generation + Visuals")

# Load OpenAI API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# RSS feeds
rss_urls = {
    "NPR Education": "https://www.npr.org/rss/rss.php?id=1014",
    "Al Jazeera Top": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters World": "http://feeds.reuters.com/reuters/worldNews",
}

# Bias and credibility
bias_credibility_map = {
    "NPR Education": {"Bias": "Left", "Credibility": "High"},
    "Al Jazeera Top": {"Bias": "Center", "Credibility": "High"},
    "Reuters World": {"Bias": "Center", "Credibility": "High"},
}

# Keywords for themes
thematic_keywords = {
    "Education": ["school", "student", "university", "teacher"],
    "Technology": ["tech", "AI", "data", "software"],
    "Politics": ["election", "policy", "congress", "government"],
}

# Warrant function
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

# Parse articles
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
        all_articles.append({
            "Source": source,
            "Title": title,
            "Link": entry.link,
            "Published": entry.published if 'published' in entry else "N/A",
            "Bias": bias_credibility_map[source]["Bias"],
            "Credibility": bias_credibility_map[source]["Credibility"],
            "Theme": theme,
        })

# Create DataFrame
df = pd.DataFrame(all_articles)

# Sidebar filter
selected_theme = st.sidebar.selectbox("Filter by Theme", ["All", "Education", "Technology", "Politics", "General"])
if selected_theme != "All":
    df = df[df["Theme"] == selected_theme]

# Show visuals
st.subheader("📊 Bias & Theme Distribution")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Bias Distribution")
    bias_counts = df["Bias"].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(bias_counts, labels=bias_counts.index, autopct="%1.1f%%", startangle=90)
    ax1.axis("equal")
    st.pyplot(fig1)

with col2:
    st.markdown("### Theme Distribution")
    theme_counts = df["Theme"].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.bar(theme_counts.index, theme_counts.values)
    ax2.set_ylabel("Number of Articles")
    ax2.set_xlabel("Theme")
    ax2.set_title("Articles by Theme")
    st.pyplot(fig2)

# Display articles
st.dataframe(df[["Source", "Title", "Published", "Bias", "Credibility", "Theme"]])

# Expandable article view
st.subheader("🔍 Explore Articles & Generate Warrants")
for index, row in df.iterrows():
    with st.expander(row["Title"]):
        st.write(f"**Source:** {row['Source']} | Published: {row['Published']}")
        st.write(f"**Bias:** {row['Bias']} | **Credibility:** {row['Credibility']} | **Theme:** {row['Theme']}")
        st.markdown(f"[Read Full Article]({row['Link']})")

        if st.button(f"🧠 Generate Warrant for: {row['Title']}", key=row['Title']):
            with st.spinner("Analyzing article..."):
                warrant = generate_warrant(row["Title"], row["Source"], row["Theme"], row["Bias"])
                st.success("Warrant Generated:")
                st.write(warrant)
