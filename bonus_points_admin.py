import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

BONUS_TYPES = {
    "Current events meme": 1,
    "Presentation on a current event": "minute",  # Points per minute
    "Submit a set of 10 questions": 5,
    "Give an extemp speech to 30+ people": 10
}

def admin_bonus_tab():
    st.subheader("🎯 Add Bonus Points to Scholar")

    # Check for admin session
    if st.session_state.get("role") != "admin":
        st.error("Access denied. Only admins can submit bonus entries.")
        return

    # Load users for dropdown
    usernames = []
    try:
        with open("users.json") as f:
            user_data = json.load(f)
            usernames = sorted([u for u, info in user_data.items() if info.get("role") == "student"])
    except:
        st.warning("Unable to load users.json or parse student list.")

    if not usernames:
        st.warning("⚠️ No student users found.")
        return

    # Load existing bonus log
    if os.path.exists("bonus_logs.csv"):
        df = pd.read_csv("bonus_logs.csv")
    else:
        df = pd.DataFrame(columns=["user", "bonus_type", "points", "notes", "timestamp"])

    user = st.selectbox("Select Scholar Username", usernames)
    bonus_type = st.selectbox("Bonus Type", list(BONUS_TYPES.keys()))
    notes = st.text_area("Notes / Explanation")
    points = 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if BONUS_TYPES[bonus_type] == "minute":
        minutes = st.number_input("Length (in minutes)", min_value=1, max_value=60, value=5)
        points = minutes
    else:
        points = BONUS_TYPES[bonus_type]

    if st.button("➕ Submit Bonus Entry"):
        bonus_entry = {
            "user": user,
            "bonus_type": bonus_type,
            "points": points,
            "notes": notes,
            "timestamp": timestamp
        }

        df = pd.concat([df, pd.DataFrame([bonus_entry])], ignore_index=True)
        df.to_csv("bonus_logs.csv", index=False)
        st.success(f"✅ Added {points} points for {user} ({bonus_type})")
