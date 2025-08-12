import streamlit as st
import pandas as pd
from datetime import date
from src.task_manager import load_tasks, update_task, add_task
from src.stats import get_weekly_summary
from src.goals import load_goals, save_goals, add_goal, update_goal_status, get_goal_summary

st.set_page_config(page_title="AI Career Tracker", layout="centered")

page_bg_img = '''
<style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1629053791347-4aeaf3bc3192?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fHBhc3RlbCUyMGdyZWVufGVufDB8fDB8fHww");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        color: black !important;
    }

    /* Force black font color across all elements */
    html, body, [class*="css"]  {
        color: black !important;
    }

    /* Optional: make sidebar text black too */
    .css-1d391kg, .css-1d3z3hw, .css-1v0mbdj {
        color: black !important;
    }
</style>
'''
input_style = '''
<style>
input, textarea, select {
    background-color: #B5B35C !important;
    color: black !important;
    border: 1px solid #ccc !important;
    border-radius: 6px;
}

.stTextInput > div > input {
    background-color: #B5B35C !important;
    color: black !important;
}
.stTextArea > div > textarea {
    background-color: #B5B35C !important;
    color: black !important;
}
.stSelectbox > div > div {
    background-color: #B5B35C !important;
    color: black !important;
}
.stMultiSelect > div {
    background-color: #B5B35C !important;
    color: black !important;
}
.stDateInput > div {
    background-color: #B5B35C !important;
    color: black !important;
}
</style>
'''

st.markdown(input_style, unsafe_allow_html=True)
st.markdown(page_bg_img, unsafe_allow_html=True)
st.title("🚀 AI Career Tracker")

df = load_tasks()
today = date.today()  # Python date

# 📌 Task Entry Form
st.subheader("📌 Add New Task")
with st.form("task_form"):
    task_date = st.date_input("Task Date", value=today)
    category = st.selectbox("Category", ["Daily", "Weekly", "Monthly", "Learning", "Project", "Workout", "Networking", "Class"])
    task_text = st.text_input("Task Description")
    submitted = st.form_submit_button("Add Task")

    if submitted and task_text.strip():
        add_task(task_date, category, task_text)
        st.success("✅ Task added!")
        st.rerun()  # Your requested rerun

df["date"] = pd.to_datetime(df["date"], errors='coerce')
filtered_tasks = df[df["date"].dt.date == today]

weekly_done, weekly_total, daily_breakdown = get_weekly_summary(df)
st.sidebar.header("Weekly Stats")
st.sidebar.metric("Week Completion", f"{weekly_done}/{weekly_total}")

st.subheader(f"Tasks for {today.strftime('%A, %B %d, %Y')}")
if filtered_tasks.empty:
    st.info("No tasks for this date yet. Add one below!")
else:
    for idx, row in filtered_tasks.iterrows():
        checked = st.checkbox(f"[{row['category']}] {row['task']}", value=row["completed"], key=idx)
        if checked != row["completed"]:
            update_task(idx, "completed", checked)

st.sidebar.header("Daily Stats")
daily_total = len(filtered_tasks)
daily_done = filtered_tasks["completed"].sum()
st.sidebar.metric("Tasks Completed", f"{daily_done}/{daily_total}")

st.markdown("___")

st.header("Goals Tracker")

goals_df = load_goals()
summary = get_goal_summary(goals_df)
st.write(
    f"Total Goals: {summary['total']}, "
    f"Completed: {summary['completed']}, "
    f"In Progress: {summary['in_progress']}, "
    f"Not Started: {summary['not_started']}"
)

st.subheader("Upcoming Deadlines")
st.table(summary['upcoming'][["title", "deadline", "status"]])

st.subheader("Add a New Goal")
with st.form("add_goal_form"):
    title = st.text_input("Goal Title")
    description = st.text_area("Description")
    deadline = st.date_input("Deadline")
    submitted = st.form_submit_button("Add Goal")
    if submitted and title:
        goals_df = add_goal(goals_df, title, description, deadline)
        save_goals(goals_df)
        st.success("Goal added!")
        st.rerun()

st.subheader("Update Goal Status")
for idx, row in goals_df.iterrows():
    new_status = st.selectbox(
        f"{row['title']} (Current: {row['status']})",
        ["Not Started", "In Progress", "Completed"],
        index=["Not Started", "In Progress", "Completed"].index(row["status"]),
        key=f"status_{row['id']}"
    )
    if new_status != row["status"]:
        goals_df = update_goal_status(goals_df, row["id"], new_status)
        save_goals(goals_df)
        st.rerun()
