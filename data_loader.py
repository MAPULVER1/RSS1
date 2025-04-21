
import pandas as pd

def load_scholar_logs(filepath="scholar_logs.csv"):
    try:
        df = pd.read_csv(filepath)
        if "bonus_points" not in df.columns:
            df["bonus_points"] = 0
        if "subject" not in df.columns:
            df["subject"] = "Unspecified"
        if "points_awarded" not in df.columns:
            df["points_awarded"] = 0
        return df
    except Exception as e:
        print(f"[load_scholar_logs] Error: {e}")
        return pd.DataFrame()

def load_bonus_logs(filepath="bonus_logs.csv"):
    try:
        df = pd.read_csv(filepath)
        if "points_awarded" not in df.columns:
            df["points_awarded"] = 0
        return df
    except Exception as e:
        print(f"[load_bonus_logs] Error: {e}")
        return pd.DataFrame()

def get_user_logs(user, df=None):
    if df is None:
        df = load_scholar_logs()
    return df[df["user"] == user]

def get_summary(df=None):
    if df is None:
        df = load_scholar_logs()
    df["Total Points"] = df["points_awarded"].fillna(0) + df["bonus_points"].fillna(0)
    return df.groupby("user").agg(
        Logs_Submitted=("title", "count"),
        Total_Points=("Total Points", "sum"),
        Regular_Points=("points_awarded", "sum"),
        Bonus_Points=("bonus_points", "sum"),
        Top_Subject=("subject", lambda x: x.mode()[0] if not x.mode().empty else "N/A")
    ).reset_index()
