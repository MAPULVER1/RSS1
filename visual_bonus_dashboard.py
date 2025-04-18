import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data(ttl=300)
def load_logs():
    try:
        df = pd.read_csv("scholar_logs.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except:
        return pd.DataFrame(columns=["user", "points_awarded", "timestamp"])

@st.cache_data(ttl=300)
def load_bonus():
    try:
        df = pd.read_csv("bonus_logs.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    except:
        return pd.DataFrame(columns=["user", "points", "timestamp"])

def visual_bonus_dashboard():
    st.title("📊 Total Participation: Regular + Bonus")

    logs = load_logs()
    bonus = load_bonus()

    regular = logs.groupby("user")["points_awarded"].sum().reset_index(name="Regular Points")
    bonus_totals = bonus.groupby("user")["points"].sum().reset_index(name="Bonus Points")

    combined = pd.merge(regular, bonus_totals, on="user", how="outer").fillna(0)
    combined = combined.infer_objects(copy=False)
    combined["Total Points"] = combined["Regular Points"] + combined["Bonus Points"]
    combined = combined.sort_values("Total Points", ascending=False)

    fig = px.bar(combined, x="user", y=["Regular Points", "Bonus Points"],
                 title="📊 Total Points by Scholar",
                 labels={"value": "Points", "user": "Scholar", "variable": "Type"},
                 barmode="stack")
    st.plotly_chart(fig, use_container_width=True)

    logs["date_only"] = logs["timestamp"].dt.normalize()
    timeline = logs.groupby("date_only").size().reset_index(name="Submissions")
    line_chart = px.line(timeline, x="date_only", y="Submissions",
                     title="🕒 Submission Activity Over Time",
                     markers=True)

    line_chart = px.line(timeline, x="timestamp", y="Submissions",
                         title="🕒 Submission Activity Over Time",
                         markers=True)
    st.plotly_chart(line_chart, use_container_width=True)
