
import pandas as pd
import subprocess
import streamlit as st
import os
from data_loader import load_scholar_logs, get_user_logs, get_summary

if "GITHUB_TOKEN" in st.secrets:
    os.environ["GITHUB_TOKEN"] = st.secrets["GITHUB_TOKEN"]

df = load_scholar_logs()
user_df = get_user_logs("gabe", df)
summary_df = get_summary(df)

def auto_git_push():
    try:
        username = st.secrets["github_username"]
        token = st.secrets["github_token"]
        repo = st.secrets["github_repo"]
        remote_url = f"https://{username}:{token}@github.com/{username}/{repo}.git"

        subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🔄 Auto update from peer question tab"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)

        st.success("✅ GitHub push complete.")
    except Exception as e:
        st.warning(f"Auto push failed: {e}")

def peer_question_tab():
    st.header("❓ Peer-Submitted Question Sets")

    # Ensure the file exists
    if not os.path.exists("bonus_logs.csv"):
        st.info("No bonus logs found yet.")
        return

    try:
        df = pd.read_csv("bonus_logs.csv")

        # Check if 'bonus_type' column exists
        if "bonus_type" not in df.columns:
            st.warning("⚠️ The 'bonus_type' column is missing from bonus logs.")
            return

        # Filter for "Submit a set of 10 questions"
        questions_df = df[df["bonus_type"] == "Submit a set of 10 questions"]

        if questions_df.empty:
            st.info("No question sets submitted yet.")
        else:
            st.markdown("### 📚 Submitted Sets of 10 Questions")
            for _, row in questions_df.iterrows():
                st.markdown(f"**{row['user']}** at _{row['timestamp']}_")
                st.markdown(f"- {row['notes']}")
                st.markdown("---")

    except Exception as e:
        st.error(f"Unable to load question data: {e}")
