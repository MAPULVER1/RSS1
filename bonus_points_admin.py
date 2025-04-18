
import streamlit as st
import pandas as pd
from datetime import datetime
import json

BONUS_TYPES = {
    "Current events meme": 1,
    "Presentation on a current event": "timed",
    "Submit a set of 10 questions": 5,
    "Extemp speech to 30+ people": 10
}

def admin_bonus_tab():
    st.markdown("### 🎯 Award Bonus Points to Scholars")

    try:
        with open("users.json") as f:
            usernames = [k for k, v in json.load(f).items() if v["role"] == "student"]
    except:
        usernames = []

    selected_user = st.selectbox("Choose Scholar", usernames)

    bonus_type = st.selectbox("Bonus Type", list(BONUS_TYPES.keys()))
    explanation = st.text_area("Reason for Bonus", placeholder="Describe the meme, presentation, or speech...")

    minutes = 0
    if BONUS_TYPES[bonus_type] == "timed":
        minutes = st.number_input("Length (in minutes)", min_value=1, max_value=120, value=5)
        points = minutes
    else:
        points = BONUS_TYPES[bonus_type]

    if st.button("💾 Submit Bonus Entry"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        bonus_entry = {
            "user": selected_user,
            "type": bonus_type,
            "points": points,
            "reason": explanation,
            "timestamp": now
        }
        try:
            df = pd.read_csv("bonus_logs.csv")
        except:
            df = pd.DataFrame(columns=list(bonus_entry.keys()))

        df = pd.concat([df, pd.DataFrame([bonus_entry])], ignore_index=True)
        df.to_csv("bonus_logs.csv", index=False)
        st.success("Bonus points submitted and recorded.")

    st.markdown("### 📋 All Bonus Logs")
    try:
        logs = pd.read_csv("bonus_logs.csv")
        logs["timestamp"] = pd.to_datetime(logs["timestamp"])
        st.dataframe(logs.sort_values("timestamp", ascending=False))
    except:
        st.info("No bonus logs recorded yet.")
