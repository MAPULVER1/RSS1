
import streamlit as st
import pandas as pd
import feedparser
import openai
from openai import OpenAI
from datetime import datetime
import plotly.express as px
import os

st.set_page_config(page_title="PulverLogic RSS", layout="wide")
st.title("🗞️ PulverLogic News Intelligence Platform")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

@st.cache_data(ttl=3600)
def fetch_live_headlines():
    rss_urls = {
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
    bias_tags = {source: "Center" for source in rss_urls}
    credibility_tags = {source: "News Source (Credentialed, Independent)" for source in rss_urls}
    today = datetime.today().strftime("%Y-%m-%d")
    entries = []
    for source, url in rss_urls.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            subject = tag_subject(entry.title)
            entries.append({
                "Date": today,
                "Source": source,
                "Title": entry.title,
                "Link": entry.link,
                "Bias": bias_tags.get(source, "Unspecified"),
                "Credibility": credibility_tags.get(source, "Unverified"),
                "Subject": subject
            })
    return pd.DataFrame(entries)

@st.cache_data(show_spinner=False)
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

# Load archive
archive_file = "rss_archive.csv"
if os.path.exists(archive_file):
    df_archive = pd.read_csv(archive_file)
    st.write("Archive shape:", df_archive.shape)
    st.dataframe(df_archive.head())
    df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
else:
    df_archive = pd.DataFrame(columns=["Date", "Source", "Title", "Link", "Subject", "Subject Confidence"])

df_today = fetch_live_headlines()

section = st.sidebar.radio("Navigate", ["📰 Top Headlines", "📊 Visual Trends", "📂 Archive Tools"])

if section == "📰 Top Headlines":
    st.subheader("📰 Explore Live Headlines by Subject")
    if not df_today.empty:
        subject_filter = st.selectbox("Filter by Subject", ["All"] + sorted(df_today["Subject"].unique()))
        filtered_today = df_today[df_today["Subject"] == subject_filter] if subject_filter != "All" else df_today
        selected = st.selectbox("Choose a headline", filtered_today["Title"].tolist())
        row = filtered_today[filtered_today["Title"] == selected].iloc[0]
        st.markdown(f"#### {row['Title']}")
        st.caption(f"{row['Source']} • {row['Date']} • Bias: {row['Bias']} • Credibility: {row['Credibility']} • Subject: {row['Subject']}")
        st.markdown(f"[🔗 Read Article]({row['Link']})")
        if st.button("🧠 Generate Warrant"):
            with st.spinner("Generating warrant..."):
                warrant = generate_warrant(row["Title"], row["Source"], row["Subject"], row["Bias"])
                st.success("Claim + Warrant:")
                st.write(warrant)
    else:
        st.info("No live headlines at the moment.")

elif section == "📊 Visual Trends":
    st.subheader("📊 Subject Mentions Over Time")
    if not df_archive.empty:
        trend_df = df_archive.groupby(["Date", "Subject"]).size().reset_index(name="Mentions")
        fig = px.line(trend_df, x="Date", y="Mentions", color="Subject", markers=True,
                      title="Trending Subjects by Date", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("#### Drill Down to Articles")
        col1, col2 = st.columns(2)
        with col1:
            chosen_subject = st.selectbox("Select subject", sorted(df_archive["Subject"].dropna().unique()))
        with col2:
            available_dates = sorted(df_archive[df_archive["Subject"] == chosen_subject]["Date"].unique())
            chosen_date = st.selectbox("Select date", available_dates)
        filtered = df_archive[(df_archive["Subject"] == chosen_subject) & (df_archive["Date"] == chosen_date)]
        for _, r in filtered.iterrows():
            st.markdown(f"- [{r['Title']}]({r['Link']})")
    else:
        st.warning("No archived data available.")

elif section == "📂 Archive Tools":
    st.subheader("📂 Search the Archive")
    if not df_archive.empty:
        subject_filter = st.selectbox("Filter by Subject", ["All"] + sorted(df_archive["Subject"].unique()))
        date_range = st.date_input("Select Date Range", [df_archive["Date"].min(), df_archive["Date"].max()])
        filtered_df = df_archive.copy()
        if subject_filter != "All":
            filtered_df = filtered_df[filtered_df["Subject"] == subject_filter]
        filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
                                  (filtered_df["Date"] <= pd.to_datetime(date_range[1]))]
        st.markdown(f"### {len(filtered_df)} Results (max 200 shown)")
        st.dataframe(filtered_df[["Date", "Title", "Source", "Subject", "Subject Confidence"]].head(200))
        st.download_button("📥 Download Archive CSV", data=filtered_df.to_csv(index=False), file_name="filtered_archive.csv")
    else:
        st.warning("No data found in archive.")
