
import streamlit as st
st.set_page_config(page_title="PulverLogic RSS", layout="wide")  # ✅ MUST be first

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

# Route authenticated users to their role-based dashboards
if st.session_state.logged_in:
    st.write("✅ Logged in — routing to role-based view")
    route_user()
else:
    # Public homepage view
    st.title("🗞️ PulverLogic RSS - Public Dashboard")
    st.markdown("Welcome to the public view. Here you can see live headlines and archived visualizations.")

    if st.button("🔐 Scholar/Admin Login"):
        login()

    try:
        df_archive = pd.read_csv("rss_archive.csv")
        df_archive["Date"] = pd.to_datetime(df_archive["Date"], errors="coerce")
        df_today = df_archive[df_archive["Date"].dt.strftime("%Y-%m-%d") == datetime.today().strftime("%Y-%m-%d")]
        st.subheader("📍 Today’s Headlines (Public Sample)")
        st.dataframe(df_today[["Date", "Title", "Source", "Subject"]].head(10))
    except:
        st.info("No public archive found.")
