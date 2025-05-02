from data_loader import load_scholar_logs

from rss_archive_tab import rss_archive_tab
from visual_bonus_dashboard import visual_bonus_dashboard
from peer_question_tab import peer_question_tab
from bonus_points_admin import admin_bonus_tab
from scholar_visual_dashboard import scholar_visual_dashboard
from rss_scholar_tab import rss_scholar_tab
import pandas as pd
import json
from datetime import datetime
from subject_filter_config import SUBJECT_OPTIONS
import streamlit as st
import os
from git_utils import safe_git_commit
from threading import Thread
from queue import Queue
import time

if "GITHUB_TOKEN" not in st.secrets:
    st.error("GitHub token is missing. Please configure it in Streamlit secrets.")
else:
    os.environ["GITHUB_TOKEN"] = st.secrets["GITHUB_TOKEN"]

# Load user access info
with open("users.json") as f:
    USERS = json.load(f)

@st.cache_data
def get_scholar_logs(data_version: str):
    return load_scholar_logs()

# Add a mechanism to invalidate the cache
data_version = os.getenv("DATA_VERSION", "1.0")  # Update this version when the data source changes

def load_logs():
    try:
        df = load_scholar_logs()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", format="%Y-%m-%d %H:%M")
        return df
    except Exception as e:
        st.warning(f"Unable to load logs: {e}")
        return pd.DataFrame()

def display_scholar_logs(df):
    st.markdown("### 📜 All Scholar Logs")
    for i, row in df.iterrows():
        with st.expander(f"{row['user']} | {row['title']}"):
            with st.form(f"admin_review_form_{i}"):
                st.markdown(f"**Link:** [{row['link']}]({row['link']})")
                st.markdown(f"**Notes:** {row['notes']}")
                admin_status = st.selectbox(
                    "Set Status", ["pending", "approved", "rejected"],
                    index=["pending", "approved", "rejected"].index(row.get("status", "pending")),
                    key=f"status_{i}"
                )
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
                submitted = st.form_submit_button("💾 Save Review")
                if submitted:
                    df.at[i, "points_awarded"] = new_points
                    df.at[i, "admin_notes"] = admin_reason
                    df.at[i, "subject"] = admin_subject
                    df.at[i, "status"] = admin_status
                    df.to_csv("scholar_logs.csv", index=False)
                    log_update_queue.put("🔄 Log update from user_access.py")
                    st.success("✅ Updated successfully.")

def login():
    st.subheader("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user["role"]
                st.rerun()
            else:
                st.error("Invalid credentials.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "public"
    st.session_state.impersonating = None
    st.rerun()

# Initialize a queue for log updates
log_update_queue = Queue()

def process_log_updates():
    while True:
        try:
            # Batch process log updates every 5 seconds
            time.sleep(5)
            if not log_update_queue.empty():
                while not log_update_queue.empty():
                    log_update_queue.get()
                safe_git_commit("🔄 Batched log updates from user_access.py")
        except Exception as e:
            print(f"Error processing log updates: {e}")

# Start the log update processing thread
Thread(target=process_log_updates, daemon=True).start()

def route_user():
    role = st.session_state.role
    if role == "admin":
        admin_dashboard()
    elif role == "student":
        scholar_dashboard(st.session_state.username)
    else:
        public_dashboard()

def admin_dashboard():
    st.sidebar.title("🧑‍💼 Admin Dashboard")
    st.sidebar.success(f"✅ Logged in as: {st.session_state.username} (Admin)")
    if st.sidebar.button("Logout", key="admin_logout"):
        logout()

    tab = st.sidebar.radio("Navigation", [
        "🎯 Bonus Points Review + Entry",
        "📈 Scholar Participation Summary",
        "📜 All Scholar Logs"
    ])

    if tab == "🎯 Bonus Points Review + Entry":
        st.markdown("### 🎯 Bonus Points Review + Entry")
        admin_bonus_tab()

    elif tab == "📈 Scholar Participation Summary":
        st.markdown("### 📈 Scholar Participation Summary")
        visual_bonus_dashboard()

    elif tab == "📜 All Scholar Logs":
        st.markdown("### 📜 All Scholar Logs")
        try:
            df = load_logs()
            # Ensure all required columns exist
            expected_cols = ["user", "title", "link", "notes", "timestamp", "points_awarded", "admin_notes", "subject"]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = ""
            display_scholar_logs(df)
        except Exception as e:
            st.warning(f"Unable to load logs: {e}")

def scholar_dashboard(username):
    st.title("🎓 Scholar Portal")
    st.success(f"✅ Logged in as: {username} (Scholar)")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📝 Submit Log", "📡 RSS Log", "📰 Today's Headlines", "👥 Peer Logs",
        "📚 My Archive", "📊 Visualize", "💡 Peer Questions"
    ])

    with tab1:
        with st.form("submit_log_form"):
            article = st.text_input("Article Title", key="article_title")
            link = st.text_input("Article Link", key="article_link")
            notes = st.text_area("Notes / Reasoning", key="article_notes")
            subject = st.selectbox("Select Subject", SUBJECT_OPTIONS, key="log_subject")
            submitted = st.form_submit_button("Submit")
            if submitted:
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                auto_score = 1 + (2 if notes and isinstance(notes, str) and len(notes) >= 100 else 0)
                entry = {
                    "user": username,
                    "title": article,
                    "link": link,
                    "notes": notes,
                    "timestamp": now,
                    "points_awarded": auto_score,
                    "admin_notes": "",
                    "subject": subject,
                    "status": "pending",
                }
                try:
                    df = get_scholar_logs(data_version)
                except KeyError:
                    if "status" not in entry:
                        entry["status"] = "pending"
                    df = pd.DataFrame(columns=list(entry.keys()))
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                df.to_csv("scholar_logs.csv", index=False)
                safe_git_commit("🔄 Log update from user_access.py")
                st.success("✅ Log submitted!")
        if st.button("Logout", key="scholar_logout"):
            logout()

    with tab2:
        rss_scholar_tab(username)

    with tab3:
        rss_archive_tab()
        st.markdown("### 📚 My Archive & Feedback")
        try:
            df = load_logs()
            user_df = df[df["user"] == username]
            st.dataframe(user_df[["timestamp", "title", "subject", "points_awarded", "admin_notes"]].sort_values("timestamp", ascending=False))
        except Exception as e:
            st.warning(f"Unable to load log data: {e}")

    with tab4:
        try:
            df = load_logs()
            peer_df = df[df["user"] != username]
            st.markdown("### 👥 View Logs from Peers")
            st.dataframe(peer_df[["timestamp", "title", "subject", "points_awarded", "admin_notes"]].sort_values("timestamp", ascending=False))
        except KeyError:
            st.info("No peer logs yet.")

    with tab5:
        df = get_scholar_logs(data_version)
        scholar_visual_dashboard(df)

    with tab6:
        peer_question_tab()

    with tab7:
        st.markdown("### 💡 Scholar Submitted Questions")
        with st.form("submit_question_form"):
            question = st.text_area("Submit a Question", key="scholar_question", max_chars=500)
            question_subject = st.selectbox("Select Subject", SUBJECT_OPTIONS, key="question_subject")
            min_questions = st.checkbox("Minimum 10 Questions Submitted", key="min_questions")
            max_questions = st.checkbox("Maximum 10 Questions Submitted", key="max_questions")
            submitted = st.form_submit_button("Submit Question")
            if submitted:
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                question_entry = {
                    "user": username,
                    "question": question,
                    "subject": question_subject,
                    "timestamp": now,
                    "status": "pending",
                    "min_questions": min_questions,
                    "max_questions": max_questions,
                }
                try:
                    df = pd.read_csv("scholar_questions.csv")
                except FileNotFoundError:
                    df = pd.DataFrame(columns=["user", "question", "subject", "timestamp", "status", "min_questions", "max_questions"])
                user_questions_count = len(df[df["user"] == username])
                if user_questions_count >= 10:
                    st.error("❌ You can only submit up to 10 questions.")
                elif not min_questions or not max_questions:
                    st.error("❌ Both minimum and maximum question submission checkboxes must be checked.")
                else:
                    df = pd.concat([df, pd.DataFrame([question_entry])], ignore_index=True)
                    df.to_csv("scholar_questions.csv", index=False)
                    safe_git_commit("🔄 Question update from user_access.py")
                    st.success("✅ Question submitted!")
        try:
            df = pd.read_csv("scholar_questions.csv")
            user_questions = df[df["user"] == username]
            st.markdown("### 📋 My Submitted Questions")
            st.dataframe(user_questions[["timestamp", "question", "subject", "status", "min_questions", "max_questions"]].sort_values("timestamp", ascending=False))
        except FileNotFoundError:
            st.info("No questions submitted yet.")
