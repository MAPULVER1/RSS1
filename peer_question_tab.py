import streamlit as st
import pandas as pd
import os

def peer_question_tab():
    st.header("❓ Peer-Submitted Question Sets")

    # Ensure the file exists
    if not os.path.exists("bonus_logs.csv"):
        st.info("No bonus logs found yet.")
        return

    try:
        df = pd.read_csv("bonus_logs.csv")

        # Check if 'type' column exists
        if "type" not in df.columns:
            st.warning("⚠️ The 'type' column is missing from bonus logs. Please ensure your CSV includes it.")
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
