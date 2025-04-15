
import streamlit as st
import pandas as pd
import os
import feedparser
from datetime import datetime, timedelta

# Set up page
st.set_page_config(page_title="PulverLogic", layout="wide")
st.title("🗞️ PulverLogic Archive Viewer")

# Use cleaned archive file
archive_file = "rss_archive_cleaned.csv"

if os.path.exists(archive_file):
    df_archive = pd.read_csv(archive_file)
    df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
else:
    df_archive = pd.DataFrame(columns=["Date", "Source", "Title", "Link", "Subject", "Subject Confidence"])

# Show summary
st.markdown("### Archive Summary")
st.write(f"Total headlines: {len(df_archive)}")
st.write(f"Date range: {df_archive['Date'].min().date()} to {df_archive['Date'].max().date()}")

# Subject trend chart
st.markdown("### 📈 Subject Mentions Over Time")
if not df_archive.empty:
    trend_df = df_archive.groupby(["Date", "Subject"]).size().reset_index(name="Mentions")
    st.dataframe(trend_df.head())

# Show top recent articles
st.markdown("### 📰 Recent Headlines")
latest = df_archive.sort_values("Date", ascending=False).head(10)
for _, row in latest.iterrows():
    st.markdown(f"- [{row['Title']}]({row['Link']}) ({row['Date'].date()}, Confidence: {row.get('Subject Confidence', 'N/A')})")
