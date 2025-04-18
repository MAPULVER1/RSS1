
import pandas as pd
import streamlit as st
import plotly.express as px
from subject_filter_config import SUBJECT_OPTIONS

# Then in Streamlit:
selected_subjects = st.multiselect("Filter by Subject", SUBJECT_OPTIONS)

def scholar_visual_dashboard():
    st.title("📊 Scholar Participation Dashboard")

    try:
        df = pd.read_csv("scholar_logs.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Total points by scholar
        points_by_user = df.groupby("user")["points_awarded"].sum().reset_index()
        points_chart = px.bar(points_by_user, x="user", y="points_awarded",
                              title="🏅 Total Points by Scholar",
                              labels={"points_awarded": "Points"},
                              color="user")
        st.plotly_chart(points_chart, use_container_width=True)

        # Logs over time
        logs_over_time = df.groupby(df["timestamp"].dt.date).size().reset_index(name="Log Count")
        logs_chart = px.line(logs_over_time, x="timestamp", y="Log Count",
                             title="🕒 Logs Submitted Over Time",
                             markers=True)
        st.plotly_chart(logs_chart, use_container_width=True)

        # Top logged subjects (if subject column added)
        if "subject" in df.columns:
            top_subjects = df["subject"].value_counts().reset_index()
            top_subjects.columns = ["Subject", "Mentions"]
            subject_chart = px.pie(top_subjects, names="Subject", values="Mentions",
                                   title="🧭 Top Logged Subjects")
            st.plotly_chart(subject_chart, use_container_width=True)

    except Exception as e:
        st.warning(f"Unable to load log data: {e}")
