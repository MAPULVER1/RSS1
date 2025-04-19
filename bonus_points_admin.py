import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
import subprocess

# Load user data
with open("users.json") as f:
    USERS = json.load(f)
scholars = [user for user, data in USERS.items() if data["role"] == "student"]

BONUS_TYPES = {
    "Current events meme": 1,
    "Presentation on a current event (time-based)": "minute",
    "Submit a set of 10 questions": 5,
    "Give an extemp speech to 30+ people": 10
}

def auto_git_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🔄 Auto log update from Streamlit app"], check=True)
        subprocess.run(["git", "push"], check=True)
    except Exception as e:
        st.warning(f"Auto push failed: {e}")

def admin_bonus_tab():
    st.subheader("🎁 Award Bonus Points (Admins Only)")

    if st.session_state.role != "admin":
        st.warning("Only admins can award bonus points.")
        return

    selected_user = st.selectbox("👤 Select Scholar", scholars)
    bonus_type = st.selectbox("🏅 Bonus Activity Type", list(BONUS_TYPES.keys()))
    notes = st.text_area("📝 Optional Notes (visible to Admins + Scholar)", max_chars=300)

    points = BONUS_TYPES[bonus_type]
    if points == "minute":
        minutes = st.number_input("⏱️ Duration in minutes", min_value=1, max_value=120)
        points = minutes

    if st.button("➕ Add Bonus Points Entry"):
        new_entry = {
            "user": selected_user,
            "bonus_type": bonus_type,
            "points": points,
            "notes": notes,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "admin": st.session_state.username
        }

        try:
            df = pd.read_csv("bonus_logs.csv")
        except FileNotFoundError:
            df = pd.DataFrame(columns=new_entry.keys())

        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv("bonus_logs.csv", index=False)

        auto_git_push()
        st.success(f"✅ Bonus points for {selected_user} recorded!")

    st.divider()
    st.markdown("### 📜 Bonus Log History")

    try:
        df = pd.read_csv("bonus_logs.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)
    except:
        st.info("No bonus point logs found yet.")

