c
import streamlit as st
import pandas as pd
import feedparser
import openai
from openai import OpenAI
from datetime import datetime
import plotly.express as px
import os

# Set up page
st.set_page_config(page_title="PulverLogic RSS", layout="wide")
st.title("🗞️ PulverLogic News Intelligence Platform")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- SUBJECT TAGGING LOGIC ---
def tag_subject(title):
    title = title.lower()
    subject_keywords = {
        "The Executive Branch": ["president", "white house", "executive", "trump"],
        "The Legislative Branch": ["congress", "senate", "house", "bill"],
        "The Judicial Branch": ["court", "judge", "justice", "ruling"],
        "Education": ["education", "school", "student", "teacher"],
        "Technology": ["ai", "innovation", "data", "software"],
        "Business & the Economy": ["inflation", "market", "finance", "jobs"],
        "World Leaders": ["putin", "xi", "modi", "zelensky"],
        "International Conflicts": ["war", "proxy", "invasion", "conflict"],
        "Business & Commerce": ["merger", "startup", "speculation", "corporate"],
        "The Global Economy": ["free trade", "exports", "imports", "tariffs"],
        "Human Rights": ["rights", "freedom", "protest", "oppression"]
    }
    for subject, keywords in subject_keywords.items():
        if any(k in title for k in keywords):
            return subject
    return "General"

# --- ARCHIVE FILE ---
archive_file = "rss_archive.csv"
if os.path.exists(archive_file):
    df_archive = pd.read_csv(archive_file)
    df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
else:
    df_archive = pd.DataFrame(columns=["Date", "Source", "Title", "Link", "Subject", "Subject Confidence"])

# --- RSS SOURCES ---
rss_urls = {
    "NPR": "https://www.npr.org/rss/rss.php?id=1001",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml"
}
bias_tags = {
    "NPR": "Left",
    "Reuters": "Center",
    "BBC News": "Center"
}
credibility_tags = {
    "NPR": "News Source (Credentialed, Independent)",
    "Reuters": "News Source (Credentialed, Independent)",
    "BBC News": "News Source (Credentialed, Independent)"
}

# --- LIVE HEADLINES ---
today = datetime.today().strftime("%Y-%m-%d")
entries = []
for source, url in rss_urls.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]:
        entries.append({
            "Date": today,
            "Source": source,
            "Title": entry.title,
            "Link": entry.link,
            "Bias": bias_tags.get(source, "Unspecified"),
            "Credibility": credibility_tags.get(source, "Unverified"),
            "Subject": tag_subject(entry.title)
        })

df_today = pd.DataFrame(entries)

# --- WARRANT GENERATOR ---
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

# --- SIDEBAR NAVIGATION ---
section = st.sidebar.radio("Navigate", ["📰 Top Headlines", "📊 Visual Trends", "📂 Archive Tools"])

# --- TOP HEADLINES ---
if section == "📰 Top Headlines":
    st.subheader("📰 Explore Live Headlines by Subject")
    if not df_today.empty:
        subject_filter = st.selectbox("Filter by Subject", ["All"] + sorted(df_today["Subject"].unique()))
        if subject_filter != "All":
            filtered_today = df_today[df_today["Subject"] == subject_filter]
        else:
            filtered_today = df_today

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

# --- VISUAL TRENDS ---
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
        if not filtered.empty:
            for _, r in filtered.iterrows():
                st.markdown(f"- [{r['Title']}]({r['Link']})")
    else:
        st.warning("No archived data available.")

# --- ARCHIVE TOOLS ---
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

        st.markdown(f"### {len(filtered_df)} Results")
        st.dataframe(filtered_df[["Date", "Title", "Source", "Subject", "Subject Confidence"]])
        st.download_button("📥 Download Archive CSV", data=filtered_df.to_csv(index=False), file_name="filtered_archive.csv")
    else:
        st.warning("No data found in archive.")
