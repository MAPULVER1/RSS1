
import streamlit as st
import pandas as pd
import plotly.express as px
from subject_filter_config import SUBJECT_OPTIONS
from data_loader import load_scholar_logs, get_summary

def scholar_visual_dashboard(df=None):
    st.title("📚 Scholar Log Overview")

    # Load data if not provided
    if df is None:
        try:
            df = load_scholar_logs()
        except Exception as e:
            st.error(f"Failed to load scholar logs: {e}")
            return

    # Display raw data
    st.write("### ✍️ Raw Scholar Log")
    if len(df) > 1000:
        st.warning("⚠️ Displaying the first 100 rows only. Consider filtering the dataset for better performance.")
    st.dataframe(df.head(100))  # Display only the first 100 rows for efficiency
    st.download_button(
        label="📥 Download Full Dataset",
        data=df.to_csv(index=False),
        file_name="scholar_logs.csv",
        mime="text/csv"
    )

    # Subject Filter
    if "subject" in df.columns:
        selected_subjects = st.multiselect("🗂️ Filter by Subject", SUBJECT_OPTIONS)
        if selected_subjects:
            df = df[df["subject"].isin(selected_subjects)]
    else:
        st.info("📘 Subject filtering is unavailable because no 'subject' column is present in the data.")

    # Scholar/Admin View Toggle
    view_mode = st.radio("👤 View Mode", ["Scholar", "Admin"], horizontal=True)

    # Points Awarded Histogram
    if "points_awarded" in df.columns:
        st.write("### 🎯 Points Awarded")
        points_chart = px.histogram(df, x="points_awarded", nbins=10, title="Distribution of Points")
        st.plotly_chart(points_chart, use_container_width=True)

    # Subject Breakdown
    if "subject" in df.columns:
        st.write("### 🧭 Subject Breakdown")
        top_subjects = df["subject"].value_counts().reset_index()
        top_subjects.columns = ["Subject", "Mentions"]
        subject_chart = px.pie(
            top_subjects,
            names="Subject",
            values="Mentions",
            title="Top Logged Subjects"
        )
        st.plotly_chart(subject_chart, use_container_width=True)

    # Feedback Notes (Admin View)
    if view_mode == "Admin" and "admin_notes" in df.columns:
        st.write("### 📝 Admin Feedback Notes")
        feedback_df = df[df["admin_notes"].notnull()][["user", "title", "admin_notes"]]
        st.dataframe(feedback_df)

    # Status Breakdown
    if "status" in df.columns:
        st.write("### 🗂️ Log Review Status")
        status_chart = px.pie(df["status"].value_counts().reset_index(),
                              names="index", values="status", title="Log Review Status Distribution")
        st.plotly_chart(status_chart, use_container_width=True)

    # Scholar-Specific Summary (Scholar View)
    if view_mode == "Scholar":
        st.write("### 📈 Your Performance Summary")
        try:
            full_df = get_summary()
            if "user" in df.columns and not df.empty:
                user = df["user"].iloc[0]
                user_summary = full_df[full_df["user"] == user]
                if not user_summary.empty:
                    st.dataframe(user_summary)
                else:
                    st.warning("No summary data available for your profile.")
        except Exception as e:
            st.error(f"Could not load performance summary: {e}")

    # Editable Feedback (Scholar View)
    if view_mode == "Scholar" and "admin_notes" in df.columns:
        st.write("### ✏️ Edit Feedback Notes")
        editable_feedback = df[["title", "admin_notes"]].copy()
        editable_feedback["admin_notes"] = editable_feedback["admin_notes"].fillna("")
        edited_feedback = st.experimental_data_editor(editable_feedback, num_rows="dynamic")
        if st.button("Save Changes"):
            try:
                # Update the original dataframe with the edited feedback
                df.update(edited_feedback)

                # Save the updated dataframe back to scholar_logs.csv
                df.to_csv("scholar_logs.csv", index=False)
                st.success("Changes saved successfully to scholar_logs.csv!")
            except Exception as e:
                st.error(f"Failed to save changes: {e}")
