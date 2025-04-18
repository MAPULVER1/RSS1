from rss_archive_tab import rss_archive_tab
from visual_bonus_dashboard import visual_bonus_dashboard
from peer_question_tab import peer_question_tab
from bonus_points_admin import admin_bonus_tab
from scholar_visual_dashboard import scholar_visual_dashboard
from rss_scholar_tab import rss_scholar_tab
import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Load user access info
with open("users.json") as f:
    USERS = json.load(f)

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

def route_user():
    role = st.session_state.role
    if role == "admin":
        admin_dashboard()
    elif role == "student":
        scholar_dashboard(st.session_state.username)
    else:
        public_dashboard()

def admin_dashboard():
    st.markdown("### 🎯 Bonus Points Review + Entry")
    admin_bonus_tab()
    st.title("🧑‍💼 Admin Dashboard")
    st.success(f"✅ Logged in as: {st.session_state.username} (Admin)")
    if st.button("Logout", key="admin_logout"):
        logout()

    st.markdown("### 📈 Scholar Participation Summary")
    visual_bonus_dashboard()

    try:
        df = pd.read_csv("scholar_logs.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        st.markdown("### 📜 All Scholar Logs")
        for i, row in df.iterrows():
            with st.expander(f"{row['user']} | {row['title']}"):
                with st.form(f"admin_review_form_{i}"):
                    st.markdown(f"**Link:** [{row['link']}]({row['link']})")
                    st.markdown(f"**Notes:** {row['notes']}")
                    new_points = st.number_input("Points", min_value=0, max_value=5, value=int(row.get("points_awarded", 0)), key=f"points_{i}")
                    admin_reason = st.text_area("Admin Notes", value=row.get("admin_notes", ""), key=f"notes_{i}")
                    admin_subject = st.selectbox("Update Subject", SUBJECT_OPTIONS, index=SUBJECT_OPTIONS.index(row.get("subject", "General")), key=f"subject_{i}")
                    save_review = st.form_submit_button("💾 Save Review")
                    if save_review:
                        df.at[i, "points_awarded"] = new_points
                        df.at[i, "admin_notes"] = admin_reason
                        df.at[i, "subject"] = admin_subject
                        df.to_csv("scholar_logs.csv", index=False)
                        st.success("✅ Updated successfully.")

    except:
        st.warning("No logs found.")

def scholar_dashboard(username):
    st.title("🎓 Scholar Portal")
    st.success(f"✅ Logged in as: {username} (Scholar)")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📝 Submit Log", "📡 RSS Log", "📰 Today's Headlines", "👥 Peer Logs",
        "📚 My Archive", "📊 Visualize", "💡 Peer Questions", "📈 Points Dashboard"
    ])

    with tab1:
        with st.form("submit_log_form"):
            article = st.text_input("Article Title", key="article_title")
            link = st.text_input("Article Link", key="article_link")
            notes = st.text_area("Notes / Reasoning", key="article_notes")
            submitted = st.form_submit_button("Submit")
            if submitted:
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                auto_score = 1 + (2 if len(notes) >= 100 else 0)
                entry = {
                    "user": username,
                    "title": article,
                    "link": link,
                    "notes": notes,
                    "timestamp": now,
                    "points_awarded": auto_score,
                    "admin_notes": ""
                }
                try:
                    df = pd.read_csv("scholar_logs.csv")
                except:
                    df = pd.DataFrame(columns=list(entry.keys()))
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                df.to_csv("scholar_logs.csv", index=False)
                st.success("✅ Log submitted!")

        if st.button("Logout", key="scholar_logout"):
            logout()

    with tab2:
        rss_scholar_tab(username)

    with tab3:
        rss_archive_tab()
        st.markdown("### 📚 My Archive & Feedback")
        try:
            df = pd.read_csv("scholar_logs.csv")
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            user_df = df[df["user"] == username]
            st.dataframe(user_df[["timestamp", "title", "points_awarded", "admin_notes"]].sort_values("timestamp", ascending=False))
        except:
            st.warning("No personal logs found.")

    with tab4:
        try:
            df = pd.read_csv("scholar_logs.csv")
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            peer_df = df[df["user"] != username]
            st.markdown("### 👥 View Logs from Peers")
            st.dataframe(peer_df.sort_values("timestamp", ascending=False))
        except:
            st.info("No peer logs yet.")

    with tab5:
        scholar_visual_dashboard()

    with tab6:
        peer_question_tab()

    with tab7:
        visual_bonus_dashboard()


def public_dashboard():
    st.title("🗞️ PulverLogic RSS - Public Dashboard")
    st.markdown("Welcome to the public view.")
    if st.button("Admin / Scholar Login", key="public_login_button"):
        login()
