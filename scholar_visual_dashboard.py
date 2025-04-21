import pandas as pd
import streamlit as st
import plotly.express as px
from subject_filter_config import SUBJECT_OPTIONS

def scholar_visual_dashboard():
    st.title("📊 Scholar Participation Dashboard")

    try:
        df = pd.read_csv("scholar_logs.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Filter by subject if available
        if "subject" in df.columns:
            top_subjects = df["subject"].value_counts().reset_index()
            top_subjects.columns = ["Subject", "Mentions"]
                subject_chart = px.pie(
                    top_subjects,
                    names="Subject",
                    title="🧭 Top Logged Subjects"
                )
    st.plotly_chart(subject_chart, use_container_width=True)
else:
    st.info("📊 Subject chart skipped — no 'subject' data found in log.")

    except Exception as e:
        st.warning(f"Unable to load log data: {e}")
