
import streamlit as st
import pandas as pd
from visual_bonus_dashboard import visual_bonus_dashboard
from scholar_visual_dashboard import scholar_visual_dashboard
from peer_question_tab import peer_question_tab
from data_loader import load_scholar_logs
from subject_filter_config import SUBJECT_OPTIONS
from git_utils import safe_git_commit

def admin_dashboard():
    st.title("🧑‍💼 Admin Dashboard")
    st.success(f"✅ Logged in as: {st.session_state.username} (Admin)")

    if st.button("Logout", key="admin_logout"):
        from user_access import logout
        logout()

    df = load_scholar_logs()
    st.markdown("### 📜 Review Logs")

    for i, row in df.iterrows():
        with st.expander(f"{row['user']} | {row['title']}"):
            with st.form(f"admin_review_form_{i}"):
                st.markdown(f"**Link:** [{row['link']}]({row['link']})")
                st.markdown(f"**Notes:** {row['notes']}")
                new_points = st.number_input(
                    "Points", min_value=0, max_value=5,
                    value=int(row.get("points_awarded", 0)),
                    key=f"points_{i}"
                )
                admin_reason = st.text_area(
                    "Admin Notes", value=row.get("admin_notes", ""),
                    key=f"notes_{i}"
                )
                admin_subject = st.selectbox(
                    "Update Subject", SUBJECT_OPTIONS,
                    index=SUBJECT_OPTIONS.index(row.get("subject", "General"))
                    if row.get("subject") in SUBJECT_OPTIONS else 0,
                    key=f"subject_{i}"
                )
                admin_status = st.selectbox(
                    "Status", ["pending", "approved", "rejected"],
                    index=["pending", "approved", "rejected"].index(row.get("status", "pending")),
                    key=f"status_{i}"
                )
                submitted = st.form_submit_button("💾 Save Review")
                if submitted:
                    df.at[i, "points_awarded"] = new_points
                    df.at[i, "admin_notes"] = admin_reason
                    df.at[i, "subject"] = admin_subject
                    df.at[i, "status"] = admin_status
                    df.to_csv("scholar_logs.csv", index=False)
                    safe_git_commit("🔄 Admin reviewed log update")
                    st.success("✅ Log updated.")

    st.divider()
    st.markdown("### 📊 System-Wide Scholar Visuals")
    scholar_visual_dashboard(df)

    st.divider()
    st.markdown("### 🧠 Peer Questions Feed")
    peer_question_tab()

    st.divider()
    st.markdown("### 📈 Bonus Participation Summary")
    visual_bonus_dashboard()
