import streamlit as st
st.set_page_config(page_title="PulverLogic RSS", layout="wide")

import pandas as pd
import feedparser
from datetime import datetime
from user_access import login, logout, route_user
import os
import subprocess

# Load GitHub token from Streamlit secrets
if "GITHUB_TOKEN" in st.secrets:
    os.environ["GITHUB_TOKEN"] = st.secrets["GITHUB_TOKEN"]

# -----------------------
# SESSION STATE SETUP
# -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = "public"
if "impersonating" not in st.session_state:
    st.session_state.impersonating = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False

# -----------------------
# STATUS BAR
# -----------------------
def status_bar():
    if st.session_state.logged_in:
        user = st.session_state.username
        role = st.session_state.role
        icon = "🧑‍💼" if role == "admin" else "🎓" if role == "student" else "🔐"
        st.info(f"{icon} Logged in as: {user} ({role.title()})")
    else:
        st.warning("🔓 Public Mode — You are not logged in")

status_bar()

# -----------------------
# LOAD EXISTING ARCHIVE
# -----------------------
archive_file = "rss_archive.csv"
today_str = datetime.today().strftime("%Y-%m-%d")

try:
    df_archive = pd.read_csv(archive_file)
    df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
except Exception as e:
    st.error(f"⚠️ Failed to load RSS archive: {e}")
    df_archive = pd.DataFrame(columns=["Date", "Source", "Title", "Link", "Subject"])

# -----------------------
# RSS PARSER FUNCTION
# -----------------------
def fetch_live_rss(feed_url):
    feed = feedparser.parse(feed_url)
    entries = []

    for entry in feed.entries:
        entries.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Source": feed.feed.get("title", "Unknown Source"),
            "Title": entry.get("title", "No title"),
            "Link": entry.get("link", "No link"),
            "Subject": "General"
        })
    return pd.DataFrame(entries)

# -----------------------
# GIT AUTO PUSH FUNCTION
# -----------------------
def safe_git_auto_push():
    """
    Automatically stages, commits, and pushes changes to the Git repository.
    Configures Git username and email for the commit.
    """
    try:
        # Set Git username and email
        subprocess.run(["git", "config", "user.name", "MAPULVER1"], check=True)
        subprocess.run(["git", "config", "user.email", "michaelalexanderpulver@outlook.com"], check=True)

        # Stage all changes
        subprocess.run(["git", "add", "."], check=True)
        # Commit changes with a generic message
        subprocess.run(["git", "commit", "-m", "Auto-commit: Updated RSS archive"], check=True)
        # Push changes to the remote repository
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Git operation failed: {e}")

# -----------------------
# ROUTE LOGIC
# -----------------------
if st.session_state.logged_in:
    route_user()
else:
    # Public homepage view
    st.title("🗾️ PulverLogic RSS - Public Dashboard")
    st.markdown("Welcome to the public view. Here you can see live headlines and archived visualizations.")

    if st.button("🔐 Scholar/Admin Login"):
        st.session_state.show_login = True

    if st.session_state.show_login:
        login()

    # Sidebar RSS Fetcher
    with st.sidebar:
        st.header("🔄 Live RSS Fetch")
        st.markdown("Provide an RSS feed URL to fetch live updates.")
        
        feed_url = st.text_input(
            "RSS Feed URL", 
            value="https://feeds.feedburner.com/TechCrunch/", 
            help="Enter the URL of the RSS feed you want to fetch."
        )
        
        if st.button("📅 Fetch Feed"):
            if feed_url.strip():
                df_live = fetch_live_rss(feed_url)
                st.session_state["live_rss"] = df_live
                st.success(f"Successfully fetched feed from: {feed_url}")
            else:
                st.error("Please provide a valid RSS feed URL.")

    # Show live RSS results
    if "live_rss" in st.session_state:
        st.subheader("🔞 Live RSS Feed Preview")
        st.dataframe(st.session_state["live_rss"])

        if st.button("📂 Save to Archive"):
            df_archive = pd.concat([df_archive, st.session_state["live_rss"]], ignore_index=True)
            df_archive.to_csv(archive_file, index=False)
            safe_git_auto_push()

            st.success("Feed saved to archive!")

    # Show today's archive sample
    if not df_archive.empty:
        df_today = df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == today_str]
        st.subheader("📍 Today’s Headlines (Public Sample)")
        st.dataframe(df_today[["Date", "Title", "Source", "Subject"]].head(10))
    else:
        st.info("No public archive found.")


