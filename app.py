
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

# Set page config
st.set_page_config(page_title="PulverLogic Newsfeed", layout="wide")
st.title("🗞️ PulverLogic Daily Dashboard")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Subject areas for tracking
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

# Match subject area
def tag_subject(title):
    title = title.lower()
    for subject, keywords in subject_keywords.items():
        if any(kw in title for kw in keywords):
            return subject
    return "General"

# Save archive
def archive_today_articles(df, archive_file="rss_archive.csv"):
    if os.path.exists(archive_file):
        existing = pd.read_csv(archive_file)
        combined = pd.concat([existing, df]).drop_duplicates(subset=["Date", "Title"])
    else:
        combined = df
    combined.to_csv(archive_file, index=False)

# Simulate subject trends
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

# RSS Feeds
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

# Warrant generation
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

# Collect live headlines
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

# Tabs
tab1, tab2, tab3 = st.tabs(["📰 Top Headlines", "📊 Visual Dashboard", "📂 Archive Dashboard"])

with tab1:
    st.subheader("🗂 Daily Headlines Across Sources")
    for index, row in df.iterrows():
        with st.container():
            st.markdown(f"### {row['Title']}")
            st.write(f"📍 {row['Source']} — 🕒 {row['Date']}")
            st.markdown(f"[Read Article →]({row['Link']})")
            with st.expander("🧠 Generate Warrant"):
                if st.button(f"Generate Warrant for: {row['Title']}", key=f"warrant_{index}"):
                    with st.spinner("Analyzing..."):
                        warrant = generate_warrant(row["Title"], row["Source"], row["Subject"], row["Bias"])
                        st.success("Claim + Warrant:")
                        st.write(warrant)
            st.markdown("---")

with tab2:
    st.subheader("📊 Visual Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Source Credibility Distribution")
        credibility_counts = df["Credibility"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(credibility_counts, labels=credibility_counts.index, autopct="%1.1f%%", startangle=90)
        ax1.axis("equal")
        st.pyplot(fig1)

    with col2:
        st.markdown("### Today's Subject Mentions")
        fig2, ax2 = plt.subplots()
        ax2.bar(bar_data["Subject"], bar_data["Count"], color=plt.cm.Set2.colors)
        ax2.set_ylabel("Mentions")
        ax2.set_xlabel("Subjects")
        ax2.set_title("Subject Coverage Today")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)

    st.markdown("### 📈 Monthly Subject Trendlines")
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    line_data.plot(ax=ax3, color=plt.cm.Set1.colors)
    ax3.set_ylabel("Mentions per Day")
    ax3.set_xlabel("Date")
    ax3.set_title("Subject Trends Over the Last Month")
    ax3.legend(title="Subjects", bbox_to_anchor=(1.05, 1), loc='upper left')
    fig3.tight_layout()
    st.pyplot(fig3)


with tab3:
    
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    
    # Load archived data
    archive_file = "rss_archive.csv"
    try:
        archive_df = pd.read_csv(archive_file)
        archive_df["Date"] = pd.to_datetime(archive_df["Date"])
    except FileNotFoundError:
        archive_df = pd.DataFrame(columns=["Date", "Source", "Title", "Link", "Bias", "Credibility", "Subject"])
    
    # Archive tab
    st.subheader("🗃️ Archive Dashboard")
    
    if archive_df.empty:
        st.warning("No archive data found yet.")
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            subject_filter = st.selectbox("Filter by Subject", ["All"] + sorted(archive_df["Subject"].unique().tolist()))
        with col2:
            date_range = st.date_input("Date Range", [archive_df["Date"].min(), archive_df["Date"].max()])
    
        filtered_df = archive_df.copy()
        if subject_filter != "All":
            filtered_df = filtered_df[filtered_df["Subject"] == subject_filter]
        filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
                                  (filtered_df["Date"] <= pd.to_datetime(date_range[1]))]
    
        # Display filtered data
        st.markdown(f"### Showing {len(filtered_df)} articles")
        st.dataframe(filtered_df[["Date", "Title", "Source", "Subject", "Bias", "Credibility"]])
    
        # Download option
        st.download_button("📥 Download Filtered Articles (CSV)", data=filtered_df.to_csv(index=False), file_name="filtered_articles.csv")
    
        # Line chart for selected subject over time
        if not filtered_df.empty:
            trend = filtered_df.groupby(["Date", "Subject"]).size().unstack(fill_value=0)
            fig, ax = plt.subplots(figsize=(10, 4))
            trend.plot(ax=ax)
            ax.set_title("📈 Subject Trends Over Time")
            ax.set_ylabel("Mentions")
            ax.set_xlabel("Date")
            st.pyplot(fig)
