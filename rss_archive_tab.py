from data_loader import load_scholar_logs
import pandas as pd
import streamlit as st
from datetime import datetime
from subject_filter_config import SUBJECT_OPTIONS
import os

def rss_archive_tab():
    st.markdown("### 📰 Today’s Headlines (from Archive)")

    archive_file = "rss_archive.csv"

    # Check if the archive file exists
    if not os.path.exists(archive_file):
        st.warning("The archive file does not exist. Please ensure the file is created.")
        return

    try:
        # Load the archive file
        df = pd.read_csv(archive_file)

        # Validate required columns
        required_columns = {"Date", "Title", "Source", "Subject", "Link"}
        if not required_columns.issubset(df.columns):
            st.error(f"The archive file is missing required columns: {required_columns - set(df.columns)}")
            return

        # Convert the Date column to datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Filter for today's headlines
        today_str = datetime.today().strftime("%Y-%m-%d")
        df_today = df[df["Date"].dt.strftime("%Y-%m-%d") == today_str]

        if df_today.empty:
            st.info("No headlines found for today.")
            return

        # Filter by selected subjects
        selected_subjects = st.multiselect("🎯 Filter by Subject", SUBJECT_OPTIONS, default=SUBJECT_OPTIONS)
        if selected_subjects:
            df_today = df_today[df_today["Subject"].isin(selected_subjects)]

        # Display the filtered DataFrame
        st.dataframe(df_today[["Date", "Title", "Source", "Subject", "Link"]])
    except Exception as e:
        st.error(f"Error loading archive: {e}")
