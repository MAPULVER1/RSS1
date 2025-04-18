
import streamlit as st
st.set_page_config(page_title="PulverLogic RSS", layout="wide")

import pandas as pd
from datetime import datetime
import os
from user_access import login, logout, route_user

# Initialize session state variables
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

# Show user status bar
def status_bar():
    if st.session_state.logged_in:
        user = st.session_state.username
        role = st.session_state.role
        if role == "admin":
            st.info(f"🧑‍💼 Logged in as: {user} (Admin)")
        elif role == "student":
            st.info(f"🎓 Logged in as: {user} (Scholar)")
        else:
            st.info(f"🔐 Logged in as: {user}")
    else:
        st.warning("🔓 Public Mode — You are not logged in")

status_bar()

# Route authenticated users to their role-based dashboards
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

    try:
        df_archive = pd.read_csv("rss_archive.csv")
        df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
        df_today = df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == datetime.today().strftime("%Y-%m-%d")]
        st.subheader("📍 Today’s Headlines (Public Sample)")
        st.dataframe(df_today[["Date", "Title", "Source", "Subject"]].head(10))
    except:
        st.info("No public archive found.")
