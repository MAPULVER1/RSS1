
import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Load user access info
with open("users.json") as f:
    USERS = json.load(f)

# Set session defaults immediately
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = "public"
if "impersonating" not in st.session_state:
    st.session_state.impersonating = None

# Login form with stable key-based inputs
def login():
    st.subheader("🔐 Login")
    st.text_input("Username", key="login_username")
    st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        username = st.session_state.login_username
        password = st.session_state.login_password
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")

# Logout
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "public"
    st.session_state.impersonating = None
    st.experimental_rerun()

# Route based on session
def route_user():
    role = st.session_state.role
    if role == "admin":
        admin_dashboard()
    elif role == "student":
        scholar_dashboard(st.session_state.username)
    else:
        public_dashboard()

# Admin view with impersonation
def admin_dashboard():
    st.title("🧑‍💼 Admin Dashboard")
    st.success(f"Logged in as: {st.session_state.username} (Admin)")
    if st.button("Logout"):
        logout()
    scholar_list = [u for u in USERS if USERS[u]["role"] == "student"]
    selected = st.selectbox("👥 Test as Scholar", scholar_list)
    if st.button("Impersonate"):
        st.session_state.impersonating = selected
        scholar_dashboard(selected)

# Scholar view
def scholar_dashboard(username):
    st.title("🎓 Scholar Portal")
    st.success(f"Logged in as: {username}")
    if st.button("Logout"):
        logout()
    st.markdown("Submit your article viewing below:")
    article = st.text_input("Article Title")
    link = st.text_input("Article Link")
    notes = st.text_area("Notes / Reasoning")
    if st.button("Submit Log"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = {"user": username, "title": article, "link": link, "notes": notes, "timestamp": now}
        try:
            df = pd.read_csv("scholar_logs.csv")
        except:
            df = pd.DataFrame(columns=["user", "title", "link", "notes", "timestamp"])
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv("scholar_logs.csv", index=False)
        st.success("Submission recorded.")

    try:
        peer_df = pd.read_csv("scholar_logs.csv")
        st.subheader("🔎 Peer Contributions")
        st.dataframe(peer_df[peer_df["user"] != username].sort_values("timestamp", ascending=False))
    except:
        st.info("No peer data yet.")

# Public fallback
def public_dashboard():
    st.title("🗞️ PulverLogic RSS - Public Dashboard")
    st.markdown("Welcome to the public view. Here you can see live headlines and archived visualizations.")
    if st.button("Admin / Scholar Login"):
        login()
