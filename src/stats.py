import pandas as pd
from datetime import datetime, timedelta

def get_weekly_summary(df: pd.DataFrame) -> tuple:
    """
    Calculates weekly completion summary from a DataFrame containing 'date' and 'completed' columns.
    
    Returns: completed_count, total_tasks, daily_breakdown_df
    """
    if df.empty:
        return 0, 0, pd.DataFrame()

    # Ensure 'date' is clean and use only necessary columns
    week_df = df.copy()
    week_df["date"] = pd.to_datetime(week_df["date"], errors='coerce').dt.normalize()
    week_df = week_df.dropna(subset=["date"])

    today = datetime.today().date()
    start = today - timedelta(days=6)
    
    # Filter for the last 7 days (start to today)
    week_df = week_df[(week_df["date"] >= pd.to_datetime(start)) & (week_df["date"] <= pd.to_datetime(today))]
    
    completed = week_df["completed"].sum()
    total = len(week_df)
    
    daily_breakdown = week_df.groupby("date")["completed"].agg(["sum", "count"]).reset_index()
    daily_breakdown.columns = ["date", "completed_count", "total_count"]
    
    return completed, total, daily_breakdown