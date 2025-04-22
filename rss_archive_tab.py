from data_loader import load_scholar_logs
import pandas as pd
import streamlit as st
from datetime import datetime
from subject_filter_config import SUBJECT_OPTIONS

def rss_archive_tab():
    st.markdown("### 📰 Today’s Headlines (from Archive)")

    try:
        df = pd.read_csv("rss_archive.csv")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        today_str = datetime.today().strftime("%Y-%m-%d")
        df_today = df[df["Date"].dt.strftime("%Y-%m-%d") == today_str]

        if df_today.empty:
            st.info("No headlines found for today.")
            return

        selected_subjects = st.multiselect("🎯 Filter by Subject", SUBJECT_OPTIONS, default=SUBJECT_OPTIONS)

        if selected_subjects:
            df_today = df_today[df_today["Subject"].isin(selected_subjects)]

        st.dataframe(df_today[["Date", "Title", "Source", "Subject", "Link"]])
    except Exception as e:
        st.error(f"Error loading archive: {e}")
