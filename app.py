import streamlit as st
st.set_page_config(page_title="PulverLogic RSS", layout="wide")

import pandas as pd
from datetime import datetime
from user_access import login, logout, route_user
import os

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
# ROUTE LOGIC
# -----------------------
if st.session_state.logged_in:
    route_user()
else:
    # Public homepage view
    st.title("🗞️ PulverLogic RSS - Public Dashboard")
    st.markdown("Welcome to the public view. Here you can see live headlines and archived visualizations.")

    if st.button("🔐 Scholar/Admin Login"):
        st.session_state.show_login = True

    if st.session_state.show_login:
        login()

    if not df_archive.empty:
        df_today = df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == today_str]
        st.subheader("📍 Today’s Headlines (Public Sample)")
        st.dataframe(df_today[["Date", "Title", "Source", "Subject"]].head(10))
    else:
        st.info("No public archive found.")

