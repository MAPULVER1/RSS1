
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

@st.cache_data(ttl=3600)
def load_archive():
    archive_file = "rss_archive.csv"
    if os.path.exists(archive_file):
        df = pd.read_csv(archive_file)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    else:
        return pd.DataFrame(columns=["Date", "Source", "Title", "Link", "Subject", "Subject Confidence", "Story Type"])

@st.cache_data(ttl=3600)
def fetch_today(df_archive):
    today_str = datetime.today().strftime("%Y-%m-%d")
    return df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == today_str]

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

df_archive = load_archive()
df_today = fetch_today(df_archive)

section = st.sidebar.radio("Navigate", ["📰 Top Headlines", "📊 Visual Trends", "📂 Archive Tools"])

if section == "📰 Top Headlines":
    st.subheader("🔥 Top of News (Fresh Headlines)")
    top_df = df_today[df_today["Story Type"] == "Top of News"]
    if not top_df.empty:
        top_selected = st.radio("Select a headline", top_df["Title"].tolist(), index=0)
        top_row = top_df[top_df["Title"] == top_selected].iloc[0]
        st.markdown(f"#### {top_row['Title']}")
        st.caption(f"{top_row['Source']} • {top_row['Date']} • {top_row['Subject']} • Confidence: {top_row['Subject Confidence']}")
        st.markdown(f"[🔗 Read Full Article]({top_row['Link']})")
        if st.button("🧠 Generate Warrant (Top Story)"):
            with st.spinner("Analyzing headline..."):
                warrant = generate_warrant(top_row["Title"], top_row["Source"], top_row["Subject"], "N/A")
                st.success("Claim + Warrant:")
                st.write(warrant)
    else:
        st.info("No fresh 'Top of News' stories yet today.")

    st.subheader("🔁 In the News (Ongoing Coverage)")
    ongoing_df = df_today[df_today["Story Type"] == "In the News"]
    if not ongoing_df.empty:
        ongoing_selected = st.selectbox("Choose an ongoing headline", ongoing_df["Title"].tolist())
        ongoing_row = ongoing_df[ongoing_df["Title"] == ongoing_selected].iloc[0]
        st.markdown(f"#### {ongoing_row['Title']}")
        st.caption(f"{ongoing_row['Source']} • {ongoing_row['Date']} • {ongoing_row['Subject']} • Confidence: {ongoing_row['Subject Confidence']}")
        st.markdown(f"[🔗 Read Full Article]({ongoing_row['Link']})")
        if st.button("🧠 Generate Warrant (Ongoing Story)"):
            with st.spinner("Analyzing headline..."):
                warrant = generate_warrant(ongoing_row["Title"], ongoing_row["Source"], ongoing_row["Subject"], "N/A")
                st.success("Claim + Warrant:")
                st.write(warrant)
    else:
        st.info("No 'In the News' entries for today.")

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
