
import streamlit as st
import pandas as pd

def peer_question_tab():
    st.markdown("### 💡 Peer-Submitted Question Sets")

    try:
        df = pd.read_csv("bonus_logs.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Filter for entries of type "Submit a set of 10 questions"
        questions_df = df[df["type"] == "Submit a set of 10 questions"]

        if questions_df.empty:
            st.info("No peer-submitted question sets available yet.")
        else:
            for _, row in questions_df.sort_values("timestamp", ascending=False).iterrows():
                st.markdown(f"**{row['user']}** submitted on `{row['timestamp'].date()}`")
                questions = row["reason"].split("\n")
                for q in questions:
                    st.markdown(f"- {q.strip()}")
                st.markdown("---")

    except FileNotFoundError:
        st.warning("No bonus log file found yet.")
