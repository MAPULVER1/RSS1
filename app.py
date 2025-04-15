
import streamlit as st
import feedparser
import pandas as pd
import openai
from openai import OpenAI
import plotly.express as px
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime, timedelta
import random
import os

# --- CONFIG ---
st.set_page_config(page_title="PulverLogic Dashboard", layout="wide")
st.title("🗞️ PulverLogic Daily News Intelligence")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- SUBJECT TAGGING SETUP ---
subject_keywords = {
    "The Legislative Branch": ["congress", "senate", "house", "bill", "lawmakers"],
    "Education": ["education", "schools", "students", "teachers", "curriculum"],
    "The Executive Branch": ["president", "white house", "biden", "executive", "cabinet"],
    "Technology": ["tech", "ai", "software", "cybersecurity", "robotics"],
    "The Judicial Branch": ["supreme court", "justice", "judge", "ruling", "legal"],
    "Business & the Economy": ["inflation", "jobs", "market", "finance", "unemployment"],
    "World Leaders": ["putin", "zelensky", "xi", "macron", "modi"],
    "International Conflicts": ["war", "conflict", "missile", "border", "diplomacy"],
    "Business & Commerce": ["merger", "startup", "retail", "stock", "ecommerce"],
    "The Global Economy": ["global", "trade", "exports", "imports", "gdp"],
    "Human Rights": ["rights", "freedom", "protest", "activists", "oppression"]
}

def tag_subject(title):
    title = title.lower()
    for subject, keywords in subject_keywords.items():
        if any(kw in title for kw in keywords):
            return subject
    return "General"

# --- ARCHIVE LOGIC ---
def archive_today_articles(df, archive_file="rss_archive.csv"):
    if os.path.exists(archive_file):
        existing = pd.read_csv(archive_file)
        combined = pd.concat([existing, df]).drop_duplicates(subset=["Date", "Title"])
    else:
        combined = df
    combined.to_csv(archive_file, index=False)

# --- TREND DATA MOCK ---
subjects = list(subject_keywords.keys())
today = datetime.today()
dates = [today - timedelta(days=i) for i in range(30)]
dates.reverse()

simulated_data = []
for date in dates:
    for subject in subjects:
        count = max(0, int(random.gauss(mu=2, sigma=1)))
        simulated_data.append({"Date": date.date(), "Subject": subject, "Count": count})
df_subjects = pd.DataFrame(simulated_data)

# --- RSS + SUBJECT LOGIC ---
rss_urls = {
    "NPR Education": "https://www.npr.org/rss/rss.php?id=1014",
    "Al Jazeera Top": "https://www.aljazeera.com/xml/rss/all.xml",
    "Reuters World": "http://feeds.reuters.com/reuters/worldNews",
}
credibility_tags = {
    "NPR Education": "News Source (Credentialed, Independent)",
    "Al Jazeera Top": "News Source (Credentialed, Independent)",
    "Reuters World": "News Source (Credentialed, Independent)",
}
bias_tags = {
    "NPR Education": "Left",
    "Al Jazeera Top": "Center",
    "Reuters World": "Center",
}

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

# --- FETCH HEADLINES ---
entries = []
for source, url in rss_urls.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]:
        subject = tag_subject(entry.title)
        entries.append({
            "Date": today.strftime("%Y-%m-%d"),
            "Source": source,
            "Title": entry.title,
            "Link": entry.link,
            "Bias": bias_tags.get(source, "Unspecified"),
            "Credibility": credibility_tags.get(source, "Unverified"),
            "Subject": subject
        })
df = pd.DataFrame(entries)
archive_today_articles(df)

# --- LOAD ARCHIVE DATA ---
archive_path = "rss_archive.csv"
if os.path.exists(archive_path):
    archive_df = pd.read_csv(archive_path)
    archive_df["Date"] = pd.to_datetime(archive_df["Date"], errors="coerce")
    archive_df.dropna(subset=["Date"], inplace=True)
else:
    archive_df = pd.DataFrame(columns=["Date", "Title", "Source", "Link", "Bias", "Credibility", "Subject"])

# --- PLOTLY TRENDS DATA ---
trend_df = archive_df.groupby(["Date", "Subject"]).size().reset_index(name="Mentions")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📰 Top Headlines", "📊 Visual Dashboard", "📂 Archive Dashboard"])

# --- TAB 1: HEADLINES ---
with tab1:
    st.markdown("### Select a headline to explore")
    selected = st.radio("📰 Select article:", df["Title"].tolist(), index=0)
    article = df[df["Title"] == selected].iloc[0]

    st.markdown(f"## {article['Title']}")
    st.write(f"**Source:** {article['Source']} | **Date:** {article['Date']}")
    st.write(f"**Subject:** {article['Subject']} | **Bias:** {article['Bias']} | **Credibility:** {article['Credibility']}")
    st.markdown(f"[🔗 Read Article]({article['Link']})")

    if st.button("🧠 Generate Warrant"):
        with st.spinner("Generating..."):
            result = generate_warrant(article["Title"], article["Source"], article["Subject"], article["Bias"])
            st.success("Claim + Warrant:")
            st.write(result)

# --- TAB 2: PLOTLY TRENDS ---
with tab2:
    st.markdown("### 📈 Subject Trends (Click to Explore)")

    fig = px.line(
        trend_df,
        x="Date",
        y="Mentions",
        color="Subject",
        title="Trends by Subject",
        template="plotly_white",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔍 Filter Articles by Date + Subject")
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.date_input("Select a Date", value=today)
    with col2:
        subject_filter = st.selectbox("Select a Subject", ["All"] + sorted(archive_df["Subject"].unique()))

    results = archive_df[archive_df["Date"] == pd.to_datetime(date_filter)]
    if subject_filter != "All":
        results = results[results["Subject"] == subject_filter]

    st.markdown(f"### {len(results)} Articles Found")
    st.dataframe(results[["Date", "Title", "Source", "Link", "Bias", "Credibility", "Subject"]])

# --- TAB 3: ARCHIVE FILTER ---
with tab3:
    st.subheader("📂 Archive Dashboard")

    if archive_df.empty:
        st.warning("No archive data available yet.")
    else:
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            sub_filter = st.selectbox("Filter by Subject", ["All"] + sorted(archive_df["Subject"].unique()))
        with fcol2:
            date_range = st.date_input("Select Date Range", [archive_df["Date"].min(), archive_df["Date"].max()])

        filtered_df = archive_df.copy()
        if sub_filter != "All":
            filtered_df = filtered_df[filtered_df["Subject"] == sub_filter]
        filtered_df = filtered_df[
            (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
            (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
        ]

        st.markdown(f"### {len(filtered_df)} Articles")
        st.dataframe(filtered_df[["Date", "Title", "Source", "Subject", "Bias", "Credibility"]])
        st.download_button("📥 Download CSV", data=filtered_df.to_csv(index=False), file_name="filtered_archive.csv")
