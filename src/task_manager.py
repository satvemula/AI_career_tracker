import os
import pandas as pd
import logging
from typing import Tuple
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class TaskManager:
    """Manages CRUD operations and statistics for daily tasks using a stable unique ID."""
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.tasks_file = os.path.join(data_dir, "tasks.csv")
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _create_empty_tasks_df(self) -> pd.DataFrame:
        """Create empty tasks DataFrame with correct schema (now including 'id')"""
        # Added 'id' as the first column
        return pd.DataFrame(columns=["id", "date", "category", "task", "completed", "created_at"])
    
    def load_tasks(self) -> pd.DataFrame:
        """Load tasks with proper error handling and validation"""
        try:
            if not os.path.exists(self.tasks_file):
                logger.info(f"Tasks file not found. Creating new one.")
                return self._create_empty_tasks_df()
            
            df = pd.read_csv(self.tasks_file)
            return self._validate_and_clean_tasks(df)
            
        except Exception as e:
            logger.error(f"Error loading tasks: {e}. Returning empty DataFrame.")
            return self._create_empty_tasks_df()
    
    def _validate_and_clean_tasks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate tasks data"""
        
        # CRITICAL INDEX FIX: Ensure every task has a unique ID
        if "id" not in df.columns or df["id"].isnull().any():
            # If 'id' is missing or has NaNs, regenerate IDs starting after the max existing ID (or 0)
            max_id = df["id"].max() if "id" in df.columns and df["id"].notnull().any() else 0
            missing_ids_count = df["id"].isnull().sum()
            
            # Assign new sequential IDs only to rows that need them
            new_ids = pd.Series(range(int(max_id) + 1, int(max_id) + 1 + missing_ids_count), 
                               index=df[df["id"].isnull()].index)
            df.loc[df["id"].isnull(), "id"] = new_ids
            
            # For older files without the column, recreate it entirely
            if "id" not in df.columns:
                 df["id"] = range(1, len(df) + 1)

        
        # Ensure correct types
        df["id"] = df["id"].astype(int)
        if "created_at" not in df.columns:
            df["created_at"] = datetime.now()
        
        # Clean data types
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["completed"] = df["completed"].fillna(False).astype(bool)
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        
        # Remove tasks with invalid dates
        df = df.dropna(subset=["date"]).reset_index(drop=True)
        
        return df
    
    def save_tasks(self, df: pd.DataFrame) -> bool:
        """Save tasks with error handling"""
        try:
            df.to_csv(self.tasks_file, index=False)
            logger.info(f"Saved {len(df)} tasks.")
            return True
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")
            return False
    
    def add_task(self, date, category: str, task: str) -> Tuple[bool, str]:
        """Add task with validation"""
        if not task.strip():
            return False, "Task description cannot be empty"
        
        df = self.load_tasks()
        # Generate new unique ID based on max existing ID
        max_id = df["id"].max() if "id" in df.columns and not df.empty else 0
        new_id = int(max_id) + 1
        
        new_task = {
            "id": new_id, # Use stable ID
            "date": pd.to_datetime(date),
            "category": category,
            "task": task.strip(),
            "completed": False,
            "created_at": datetime.now()
        }
        df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)
        
        if self.save_tasks(df):
            return True, "Task added successfully"
        else:
            return False, "Failed to save task"
    
    def update_task(self, task_id: int, column: str, value) -> bool:
        """Update task by unique ID instead of volatile DataFrame index."""
        try:
            df = self.load_tasks()
            
            # Use .loc with the unique ID to find the row reliably
            if column == "completed" and isinstance(value, bool):
                 df.loc[df["id"] == task_id, "completed"] = value
                 return self.save_tasks(df)
            else:
                 logger.warning(f"Update failed: Cannot update {column} or ID {task_id} not found.")
                 return False

        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its unique ID."""
        try:
            df = self.load_tasks()
            initial_count = len(df)
            
            # Filter the DataFrame to exclude the task with the given ID
            df = df[df["id"] != task_id]
            
            if len(df) < initial_count:
                return self.save_tasks(df)
            
            return False # Task ID not found
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False
    
    def get_task_stats(self) -> dict:
        """Get comprehensive task statistics"""
        df = self.load_tasks()
        
        if df.empty:
            return {"total": 0, "completed": 0, "completion_rate": 0, "by_category": {}}
        
        total = len(df)
        completed = df["completed"].sum()
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        # Convert grouped DataFrame to a dictionary for easier app consumption
        by_category = df.groupby("category").agg(
            total_tasks=("category", "size"),
            completed_tasks=("completed", "sum")
        ).to_dict('index')

        return {
            "total": total,
            "completed": int(completed),
            "completion_rate": round(completion_rate, 2),
            "by_category": by_category
        }