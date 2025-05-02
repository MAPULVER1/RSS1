import pandas as pd
import streamlit as st
import plotly.express as px

def visual_bonus_dashboard():
    st.title("📊 Total Participation: Regular + Bonus")

    # Load and preprocess logs
    try:
        logs = pd.read_csv("scholar_logs.csv")
        logs["timestamp"] = pd.to_datetime(logs["timestamp"], errors="coerce", format="%Y-%m-%d %H:%M")
    except FileNotFoundError:
        st.error("⚠️ 'scholar_logs.csv' not found.")
        logs = pd.DataFrame(columns=["user", "points_awarded", "timestamp"])
    except Exception as e:
        st.error(f"⚠️ Error loading 'scholar_logs.csv': {e}")
        logs = pd.DataFrame(columns=["user", "points_awarded", "timestamp"])

    try:
        bonus = pd.read_csv("bonus_logs.csv")
        bonus["timestamp"] = pd.to_datetime(bonus["timestamp"], errors="coerce", format="%Y-%m-%d %H:%M")
    except FileNotFoundError:
        st.error("⚠️ 'bonus_logs.csv' not found.")
        bonus = pd.DataFrame(columns=["user", "points", "timestamp"])
    except Exception as e:
        st.error(f"⚠️ Error loading 'bonus_logs.csv': {e}")
        bonus = pd.DataFrame(columns=["user", "points", "timestamp"])

    # Aggregate total points
    regular = logs.groupby("user", as_index=False)["points_awarded"].sum().rename(columns={"points_awarded": "Regular Points"})
    bonus_totals = bonus.groupby("user", as_index=False)["points"].sum().rename(columns={"points": "Bonus Points"})

    combined = pd.merge(regular, bonus_totals, on="user", how="outer").fillna(0)
    combined["Total Points"] = combined["Regular Points"] + combined["Bonus Points"]
    combined = combined.sort_values("Total Points", ascending=False)

    # Generate bar chart
    if not combined.empty:
        fig = px.bar(
            combined,
            x="user",
            y=["Regular Points", "Bonus Points"],
            title="📊 Total Points by Scholar",
            labels={"value": "Points", "user": "Scholar", "variable": "Type"},
            barmode="stack"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No data available to generate the chart.")

    # Generate timeline chart
    if not logs.empty and "timestamp" in logs.columns:
        timeline = logs.groupby(logs["timestamp"].dt.floor("D")).size().reset_index(name="Submissions")
        timeline.rename(columns={"timestamp": "Date"}, inplace=True)

        line_chart = px.line(
            timeline,
            x="Date",
            y="Submissions",
            title="🕒 Submission Activity Over Time",
            markers=True
        )
        st.plotly_chart(line_chart, use_container_width=True)
    else:
        st.warning("⚠️ No submission data available to generate the timeline chart.")


