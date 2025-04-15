
import streamlit as st
import feedparser
import pandas as pd
import openai
from openai import OpenAI
import matplotlib.pyplot as plt
from collections import Counter
import re
from datetime import datetime, timedelta
import random
import os

# Streamlit page config
st.set_page_config(page_title="PulverLogic Dashboard", layout="wide")
st.title("🗞️ PulverLogic Daily News Intelligence")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Subject keywords
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

def archive_today_articles(df, archive_file="rss_archive.csv"):
    if os.path.exists(archive_file):
        existing = pd.read_csv(archive_file)
        combined = pd.concat([existing, df]).drop_duplicates(subset=["Date", "Title"])
    else:
        combined = df
    combined.to_csv(archive_file, index=False)

# Simulate 30-day data
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
today_data = df_subjects[df_subjects["Date"] == today.date()]
bar_data = today_data.groupby("Subject")["Count"].sum().reset_index()
line_data = df_subjects.groupby(["Date", "Subject"])["Count"].sum().unstack(fill_value=0)

# RSS sources
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

# Live headlines
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

tab1, tab2, tab3 = st.tabs(["📰 Top Headlines", "📊 Visual Dashboard", "📂 Archive Dashboard"])

# --- TOP HEADLINES AS CLICKABLE BOXES ---
with tab1:
    st.markdown("### 🗂 Click a headline to explore")
    selected = st.radio("📰 Select article:", df["Title"].tolist(), index=0)

    article = df[df["Title"] == selected].iloc[0]
    st.markdown(f"## {article['Title']}")
    st.write(f"**Source:** {article['Source']}  |  **Date:** {article['Date']}")
    st.write(f"**Subject:** {article['Subject']}  |  **Bias:** {article['Bias']}  |  **Credibility:** {article['Credibility']}")
    st.markdown(f"[🔗 Read Article]({article['Link']})")

    if st.button("🧠 Generate Warrant"):
        with st.spinner("Generating warrant..."):
            warrant = generate_warrant(article["Title"], article["Source"], article["Subject"], article["Bias"])
            st.success("Claim + Warrant:")
            st.write(warrant)

# --- REFINED VISUAL DASHBOARD ---
with tab2:
    st.markdown("### 📊 Subject Coverage Overview")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Credibility Distribution")
        credibility_counts = df["Credibility"].value_counts()
        fig1, ax1 = plt.subplots(figsize=(4, 4))
        ax1.pie(credibility_counts, labels=credibility_counts.index, autopct="%1.1f%%", startangle=90)
        ax1.axis("equal")
        st.pyplot(fig1)

        st.markdown("#### Today’s Subjects")
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        ax2.bar(bar_data["Subject"], bar_data["Count"], color=plt.cm.Set2.colors)
        ax2.set_ylabel("Mentions")
        ax2.set_xticklabels(bar_data["Subject"], rotation=45, ha="right", fontsize=8)
        st.pyplot(fig2)

    with col2:
        st.markdown("#### Subject Trendlines (Last 30 Days)")
        fig3, ax3 = plt.subplots(figsize=(12, 5))
        line_data.plot(ax=ax3, color=plt.cm.Set1.colors)
        ax3.set_ylabel("Mentions per Day")
        ax3.set_xlabel("Date")
        ax3.set_title("Subject Trends")
        ax3.legend(title="Subjects", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        fig3.tight_layout()
        st.pyplot(fig3)

# Tab3 (Archive Dashboard) is left untouched and assumed to already be appended
