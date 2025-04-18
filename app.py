
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Load user-access-controlled routing
from user_access import login, logout, route_user

# Set up interface
st.set_page_config(page_title="PulverLogic RSS", layout="wide")

# If user is logged in, route to role-specific view
if "logged_in" in st.session_state and st.session_state.logged_in:
    route_user()
else:
    # Public homepage view
    st.title("🗞️ PulverLogic RSS - Public Dashboard")
    st.markdown("Welcome to the public view. Here you can see live headlines and archived visualizations.")

    if st.button("🔐 Scholar/Admin Login"):
        login()

    # Public summary of headlines (optional)
    try:
        df_archive = pd.read_csv("rss_archive.csv")
        df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
        df_today = df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == datetime.today().strftime("%Y-%m-%d")]
        st.subheader("📍 Today’s Headlines (Public Sample)")
        st.dataframe(df_today[["Date", "Title", "Source", "Subject"]].head(10))
    except:
        st.info("No public archive found.")
