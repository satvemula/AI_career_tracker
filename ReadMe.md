🚀 AI Career Tracker (Streamlit App)
A personal task and goal management application built with Python and Streamlit to help track career development, projects, learning, and daily productivity. All data is persisted locally in CSV files.

Key Tech: Python, Streamlit, Pandas, Plotly.

✨ Features
Modular Architecture: Uses a clean src/ folder structure with separate classes for Task and Goal management (TaskManager, GoalManager).

Interactive Dashboard: A full-featured web UI built with Streamlit for easy data input and visualization.

Data Persistence: Tasks and Goals are automatically saved to data/tasks.csv and data/goals.csv.

Analytics: Displays task completion rates, category distribution (pie chart), and weekly progress charts using Plotly.

Goal Tracking: Manages long-term goals with deadlines and status updates.

📁 Repository Structure
.
├── data/
│   ├── goals.csv         # Saved goal data (ignored by Git)
│   └── tasks.csv         # Saved task data (ignored by Git)
├── src/
│   ├── goals.py          # GoalManager class logic
│   ├── stats.py          # Utility for calculating weekly stats
│   └── task_manager.py   # TaskManager class logic
├── tracker_app.py        # Main Streamlit application entry point
└── requirements.txt      # Project dependencies
🛠️ Getting Started
1. Installation

Clone the repository:

Bash
git clone https://github.com/yourusername/ai-career-tracker.git
cd ai-career-tracker
Install dependencies:

Bash
pip install -r requirements.txt
2. Usage

Run the Streamlit application from your terminal:

Bash
streamlit run tracker_app.py
The application will automatically open in your web browser, typically at http://localhost:8501.