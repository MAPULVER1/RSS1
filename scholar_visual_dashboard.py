
import streamlit as st
import pandas as pd
import plotly.express as px
from subject_filter_config import SUBJECT_OPTIONS

def scholar_visual_dashboard(df):
    st.title("📚 Scholar Log Overview (Diagnostic Mode)")

    st.subheader("🧪 Diagnostic: DataFrame Columns")
    st.code(str(df.columns.tolist()), language='python')

    if "subject" not in df.columns:
        st.error("⚠️ 'subject' column is missing from log data.")
    else:
        st.success("✅ 'subject' column found.")

    # Subject Filter
    if "subject" in df.columns:
        selected_subjects = st.multiselect("🗂️ Filter by Subject", SUBJECT_OPTIONS)
        if selected_subjects:
            df = df[df["subject"].isin(selected_subjects)]
    else:
        st.info("📘 Subject filtering is unavailable because no 'subject' column is present in the data.")

    # Points Chart
    if "points_awarded" in df.columns:
        st.write("### 🎯 Points Awarded")
        points_chart = px.histogram(df, x="points_awarded", nbins=10, title="Distribution of Points")
        st.plotly_chart(points_chart, use_container_width=True)

    # Subject Chart
    if "subject" in df.columns:
        top_subjects = df["subject"].value_counts().reset_index()
        top_subjects.columns = ["Subject", "Mentions"]
        subject_chart = px.pie(
            top_subjects,
            names="Subject",
            values="Mentions",
            title="🧭 Top Logged Subjects"
        )
        st.plotly_chart(subject_chart, use_container_width=True)

    # Admin Feedback Notes
    if "admin_notes" in df.columns:
        st.write("### 📝 Admin Feedback Notes")
        feedback_df = df[df["admin_notes"].notnull()][["user", "title", "admin_notes"]]
        st.dataframe(feedback_df)
