
import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Load user access info
with open("users.json") as f:
    USERS = json.load(f)

# Set session defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = "public"
if "impersonating" not in st.session_state:
    st.session_state.impersonating = None

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
    st.title("🧑‍💼 Admin Dashboard")
    st.markdown("Welcome to the administrative control center.")
    st.success(f"✅ Logged in as: {st.session_state.username} (Admin)")
    if st.button("Logout", key="admin_logout"):
        logout()
    scholar_list = [u for u in USERS if USERS[u]["role"] == "student"]
    selected = st.selectbox("👥 Test as Scholar", scholar_list)
    if st.button("Impersonate", key="impersonate_button"):
        st.session_state.impersonating = selected
        scholar_dashboard(selected)

def scholar_dashboard(username):
    st.title("🎓 Scholar Portal")
    st.success(f"✅ Logged in as: {username} (Scholar)")

    tab1, tab2 = st.tabs(["📝 Submit Article Log", "📂 View Archive"])

    with tab1:
        if st.button("Logout", key="scholar_logout"):
            logout()
        st.markdown("Submit your article viewing below:")
        article = st.text_input("Article Title", key="article_title")
        link = st.text_input("Article Link", key="article_link")
        notes = st.text_area("Notes / Reasoning", key="article_notes")
        if st.button("Submit Log", key="submit_log"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_entry = {"user": username, "title": article, "link": link, "notes": notes, "timestamp": now}
            try:
                df = pd.read_csv("scholar_logs.csv")
            except:
                df = pd.DataFrame(columns=["user", "title", "link", "notes", "timestamp"])
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv("scholar_logs.csv", index=False)
            st.success("Submission recorded.")

    with tab2:
        st.markdown("### Scholar Log Archive")
        try:
            df = pd.read_csv("scholar_logs.csv")
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df[df["user"] == username]
            date_range = st.date_input("Date Range", [df["timestamp"].min(), df["timestamp"].max()])
            df = df[(df["timestamp"] >= pd.to_datetime(date_range[0])) & (df["timestamp"] <= pd.to_datetime(date_range[1]))]
            st.dataframe(df.sort_values("timestamp", ascending=False))
            st.download_button("📥 Download Your Logs", data=df.to_csv(index=False), file_name="my_logs.csv")
        except:
            st.info("No archive entries found.")

def public_dashboard():
    st.title("🗞️ PulverLogic RSS - Public Dashboard")
    st.markdown("Welcome to the public view. Here you can see live headlines and archived visualizations.")
    if st.button("Admin / Scholar Login", key="public_login_button"):
        login()
