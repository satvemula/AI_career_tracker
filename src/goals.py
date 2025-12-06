import os
import pandas as pd
from datetime import datetime

class GoalManager:
    """Manages career goals, deadlines, and status tracking."""
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.goals_file = os.path.join(data_dir, "goals.csv")
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
    def _create_empty_goals_df(self):
        """Create empty goals DataFrame with correct schema"""
        return pd.DataFrame(columns=["id", "title", "description", "deadline", "status"])

    def load_goals(self):
        """Load goals from CSV file."""
        try:
            df = pd.read_csv(self.goals_file, parse_dates=["deadline"])
            # Ensure proper types
            df["status"] = df["status"].astype(str)
            df["deadline"] = pd.to_datetime(df["deadline"], errors='coerce')
        except FileNotFoundError:
            df = self._create_empty_goals_df()
        return df

    def save_goals(self, df):
        """Save goals DataFrame to CSV file."""
        df.to_csv(self.goals_file, index=False)

    def add_goal(self, title, description, deadline, status="Not Started"):
        """Add a new goal to the DataFrame with a unique id."""
        df = self.load_goals()
        new_id = df["id"].max() + 1 if not df.empty else 1
        new_goal = {
            "id": new_id,
            "title": title,
            "description": description,
            "deadline": pd.to_datetime(deadline),
            "status": status
        }
        df = pd.concat([df, pd.DataFrame([new_goal])], ignore_index=True)
        self.save_goals(df)

    def update_goal_status(self, goal_id, new_status):
        """Update the status of a goal by id."""
        df = self.load_goals()
        df.loc[df["id"] == goal_id, "status"] = new_status
        self.save_goals(df)
        
    def get_goal_summary(self):
        """Generate summary statistics for goals including counts and upcoming goals."""
        df = self.load_goals()
        if df.empty:
             return {"total": 0, "completed": 0, "in_progress": 0, "not_started": 0, "upcoming": pd.DataFrame()}
             
        total = len(df)
        completed = len(df[df["status"] == "Completed"])
        in_progress = len(df[df["status"] == "In Progress"])
        not_started = len(df[df["status"] == "Not Started"])
        
        # Upcoming goals must be on or after today
        today = pd.Timestamp(datetime.today().date())
        upcoming = df[(df["deadline"] >= today) & (df["status"] != "Completed")]
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "upcoming": upcoming.sort_values("deadline")
        }