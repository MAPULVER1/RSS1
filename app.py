
import streamlit as st
import pandas as pd
import feedparser
import openai
from openai import OpenAI
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import plotly.express as px

# Config
st.set_page_config(page_title="PulverLogic RSS", layout="wide")
st.title("🗞️ PulverLogic News Intelligence Platform")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Use cleaned archive file
archive_file = "rss_archive_cleaned.csv"
if os.path.exists(archive_file):
    df_archive = pd.read_csv(archive_file)
    df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
else:
    df_archive = pd.DataFrame(columns=["Date", "Source", "Title", "Link", "Subject", "Subject Confidence"])

# RSS sources
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

# Generate warrant (used in Top Headlines)
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

# Collect current headlines
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
            "Subject": "General"
        })

df_today = pd.DataFrame(entries)

# UI Tabs
tab1, tab2, tab3 = st.tabs(["📰 Top Headlines", "📊 Visual Dashboard", "📂 Archive Dashboard"])

# --- TOP HEADLINES ---
with tab1:
    st.markdown("### Select and Explore an Article")
    if not df_today.empty:
        selected = st.radio("Select headline", df_today["Title"].tolist(), index=0)
        row = df_today[df_today["Title"] == selected].iloc[0]
        st.markdown(f"## {row['Title']}")
        st.write(f"📍 {row['Source']} | 🗓 {row['Date']}")
        st.write(f"🧭 Subject: {row['Subject']} | Bias: {row['Bias']} | Credibility: {row['Credibility']}")
        st.markdown(f"[🔗 Read Full Article]({row['Link']})")
        if st.button("🧠 Generate Warrant"):
            with st.spinner("Analyzing headline..."):
                warrant = generate_warrant(row["Title"], row["Source"], row["Subject"], row["Bias"])
                st.success("Claim + Warrant:")
                st.write(warrant)
    else:
        st.info("No live headlines available at the moment.")

# --- VISUAL DASHBOARD ---
with tab2:
    st.markdown("### 📊 Interactive Subject Trends")
    if not df_archive.empty:
        trend_df = df_archive.groupby(["Date", "Subject"]).size().reset_index(name="Mentions")
        fig = px.line(trend_df, x="Date", y="Mentions", color="Subject", markers=True,
                      title="Subject Mentions Over Time", labels={"Mentions": "Article Count"},
                      template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Filter Articles by Date + Subject")
        col1, col2 = st.columns(2)
        with col1:
            chosen_subject = st.selectbox("Choose subject", sorted(df_archive["Subject"].dropna().unique()))
        with col2:
            date_opts = sorted(df_archive[df_archive["Subject"] == chosen_subject]["Date"].unique())
            chosen_date = st.selectbox("Choose date", date_opts)

        filtered = df_archive[(df_archive["Subject"] == chosen_subject) & (df_archive["Date"] == chosen_date)]
        if not filtered.empty:
            st.markdown(f"#### Articles on {chosen_subject} ({chosen_date.date()})")
            for _, r in filtered.iterrows():
                st.markdown(f"- [{r['Title']}]({r['Link']})")
    else:
        st.info("No archived data available for visualization.")

# --- ARCHIVE DASHBOARD ---
with tab3:
    st.markdown("### 🗃️ Archived Headlines")
    if not df_archive.empty:
        subject_filter = st.selectbox("Filter by Subject", ["All"] + sorted(df_archive["Subject"].unique()))
        date_range = st.date_input("Select Date Range", [df_archive["Date"].min(), df_archive["Date"].max()])
        filtered_df = df_archive.copy()
        if subject_filter != "All":
            filtered_df = filtered_df[filtered_df["Subject"] == subject_filter]
        filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
                                  (filtered_df["Date"] <= pd.to_datetime(date_range[1]))]
        st.write(f"Showing {len(filtered_df)} results")
        st.dataframe(filtered_df[["Date", "Title", "Source", "Subject", "Subject Confidence"]])
        st.download_button("📥 Export CSV", data=filtered_df.to_csv(index=False), file_name="filtered_archive.csv")
    else:
        st.info("No archive data available.")
