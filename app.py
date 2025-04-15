
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

# Set Streamlit page settings
st.set_page_config(page_title="PulverLogic Newsfeed", layout="wide")
st.title("🗞️ PulverLogic Daily Dashboard")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Define academic subjects
subjects = ["Immigration Policy", "Trump Administration", "Russia", "China", "Healthcare"]

# Simulate one-month history of headlines
today = datetime.today()
dates = [today - timedelta(days=i) for i in range(30)]
dates.reverse()

simulated_data = []
for date in dates:
    for subject in subjects:
        count = max(0, int(random.gauss(mu=2, sigma=1)))
        simulated_data.append({"Date": date.date(), "Subject": subject, "Count": count})

df_subjects = pd.DataFrame(simulated_data)

# Summarize for today's bar chart
today_data = df_subjects[df_subjects["Date"] == today.date()]
bar_data = today_data.groupby("Subject")["Count"].sum().reset_index()

# Summarize for monthly line chart
line_data = df_subjects.groupby(["Date", "Subject"])["Count"].sum().unstack(fill_value=0)

# RSS Feeds and metadata
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

# Fetch live articles
all_articles = []
for source, url in rss_urls.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]:
        all_articles.append({
            "Source": source,
            "Title": entry.title,
            "Link": entry.link,
            "Published": entry.published if 'published' in entry else "N/A",
            "Bias": bias_tags.get(source, "Unspecified"),
            "Credibility": credibility_tags.get(source, "Unverified / Blog / Aggregator")
        })
df = pd.DataFrame(all_articles)

# Tabs for navigation
tab1, tab2 = st.tabs(["📰 Top Headlines", "📊 Visual Dashboard"])

# --- HEADLINES TAB ---
with tab1:
    st.subheader("🗂 Daily Headlines Across Sources")
    for index, row in df.iterrows():
        with st.container():
            st.markdown(f"### {row['Title']}")
            st.write(f"📍 {row['Source']} — 🕒 {row['Published']}")
            st.markdown(f"[Read Article →]({row['Link']})")
            with st.expander("🧠 Generate Warrant"):
                if st.button(f"Generate Warrant for: {row['Title']}", key=f"warrant_{index}"):
                    with st.spinner("Analyzing..."):
                        warrant = generate_warrant(row["Title"], row["Source"], "Unspecified", row["Bias"])
                        st.success("Claim + Warrant:")
                        st.write(warrant)
            st.markdown("---")

# --- VISUAL DASHBOARD TAB ---
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
