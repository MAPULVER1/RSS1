# Finalized function to drop into user_access.py or visual_bonus_dashboard.py
admin_dashboard_code = """
import streamlit as st
import pandas as pd
from visual_bonus_dashboard import visual_bonus_dashboard
from scholar_visual_dashboard import scholar_visual_dashboard
from peer_question_tab import peer_question_tab

def summarize_student_performance(df):
    df["Total Points"] = df["points_awarded"].fillna(0) + df.get("bonus_points", 0).fillna(0)
    return df.groupby("user").agg(
        Logs_Submitted=("title", "count"),
        Total_Points=("Total Points", "sum"),
        Regular_Points=("points_awarded", "sum"),
        Bonus_Points=("bonus_points", "sum"),
        Top_Subject=("subject", lambda x: x.mode()[0] if not x.mode().empty else "N/A")
    ).reset_index()

def admin_dashboard():
   
