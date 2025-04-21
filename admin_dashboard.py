# Finalized function to drop into user_access.py or visual_bonus_dashboard.py
admin_dashboard_code = """
import streamlit as st
import pandas as pd
from visual_bonus_dashboard import visual_bonus_dashboard
from scholar_visual_dashboard import scholar_visual_dashboard
from peer_question_tab import peer_question_tab

def summarize_student_performance(df):
    df["Total Points"] = df["points_awarded"].fillna(0) + df.get("bonus_points", 0).fillna(0)
    return df.groupby("user").agg(
        Logs_Submitted=("title", "count"),
        Total_Points=("Total Points", "sum"),
        Regular_Points=("points_awarded", "sum"),
        Bonus_Points=("bonus_points", "sum"),
        Top_Subject=("subject", lambda x: x.mode()[0] if not x.mode().empty else "N/A")
    ).reset_index()

def admin_dashboard():
    st.title("🧑‍💼 Admin Dashboard")

    # View toggle
    view_mode = st.radio("🔀 View As", ["Admin Panel", "Student View"])

    if view_mode == "Admin Panel":
        st.subheader("📊 Student Performance Summary")
        try:
            df = pd.read_csv("scholar_logs.csv")
            if "bonus_points" not in df.columns:
                df["bonus_points"] = 0
            summary = summarize_student_performance(df)

            def highlight_low(row):
                color = "background-color: #ffe6e6" if row["Total_Points"] < 5 else ""
                return [color] * len(row)

            st.dataframe(summary.style.apply(highlight_low, axis=1))
        except Exception as e:
            st.error(f"Could not load scholar logs: {e}")

        st.divider()
        visual_bonus_dashboard()

    elif view_mode == "Student View":
        try:
            df = pd.read_csv("scholar_logs.csv")
            scholar_visual_dashboard(df)
        except Exception as e:
            st.error(f"Student view error: {e}")

        st.divider()
        peer_question_tab()
"""

# Save to file so user can drop it into user_access.py or call from admin route
admin_dashboard_path = "/mnt/data/admin_dashboard.py"
with open(admin_dashboard_path, "w") as f:
    f.write(admin_dashboard_code)

admin_dashboard_path
