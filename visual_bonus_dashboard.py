import pandas as pd
import streamlit as st
import plotly.express as px

def visual_bonus_dashboard():
    st.title("📊 Total Participation: Regular + Bonus")

    try:
        logs = pd.read_csv("scholar_logs.csv")
        logs["timestamp"] = pd.to_datetime(logs["timestamp"], errors="coerce", format="%Y-%m-%d %H:%M")
    except:
        logs = pd.DataFrame(columns=["user", "points_awarded", "timestamp"])

    try:
        bonus = pd.read_csv("bonus_logs.csv")
        bonus["timestamp"] = pd.to_datetime(bonus["timestamp"], errors="coerce", format="%Y-%m-%d %H:%M")
    except:
        bonus = pd.DataFrame(columns=["user", "points", "timestamp"])

    # Aggregate total points
    regular = logs.groupby("user")["points_awarded"].sum().reset_index(name="Regular Points")
    bonus_totals = bonus.groupby("user")["points"].sum().reset_index(name="Bonus Points")

    combined = pd.merge(regular, bonus_totals, on="user", how="outer").fillna(0).infer_objects(copy=False)
    combined = combined.infer_objects(copy=False)
    combined["Total Points"] = pd.to_numeric(combined["Regular Points"], errors="coerce").fillna(0) + pd.to_numeric(combined["Bonus Points"], errors="coerce").fillna(0)
    combined = combined.sort_values("Total Points", ascending=False)

    if not combined.empty and 'User' in combined.columns and 'Total Points' in combined.columns:
        fig = px.bar(combined, x='User', y='Total Points', title='Total Points by User')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning('⚠️ Cannot generate chart: missing or invalid data.')
    st.plotly_chart(fig, use_container_width=True)

    if not logs.empty and "timestamp" in logs.columns:
        timeline = logs.groupby(logs["timestamp"].dt.floor("D")).size().reset_index(name="Submissions")
        timeline.rename(columns={timeline.columns[0]: "date_only"}, inplace=True)

        line_chart = px.line(
            timeline,
            x="date_only",
            y="Submissions",
            title="🕒 Submission Activity Over Time",
            markers=True
        )
        st.plotly_chart(line_chart, use_container_width=True)


