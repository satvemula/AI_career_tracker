import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import logging

# --- IMPORT CLEANUP ---
# Assuming you have the TaskManager, GoalManager, and get_weekly_summary available
from src.task_manager import TaskManager
from src.goals import GoalManager # Assuming you refactored goals.py into a class
from src.stats import get_weekly_summary
# ----------------------

# Configure page
st.set_page_config(
    page_title="AI Career Tracker", 
    layout="wide",  # Changed to wide for better layout
    initial_sidebar_state="expanded"
)

# Enhanced styling
def set_page_style(theme_name):
    """Sets the custom CSS style based on the selected theme."""
    
    # Define color schemes
    if theme_name == "Dark":
        bg_gradient = 'linear-gradient(135deg, #2c3e50 0%, #34495e 100%)'
        text_color = 'white'
        card_bg = 'rgba(255, 255, 255, 0.1)'
        border_color = '#3498db'
    elif theme_name == "Light":
        bg_gradient = 'linear-gradient(135deg, #ecf0f1 0%, #bdc3c7 100%)'
        text_color = 'black'
        card_bg = 'rgba(0, 0, 0, 0.1)'
        border_color = '#2980b9'
    else:  # Default/Original Green Theme
        bg_gradient = 'linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%)'
        text_color = 'black'
        card_bg = 'rgba(255, 255, 255, 0.15)'
        border_color = '#4CAF50'

    page_style = f'''
    <style>
        .stApp {{
            background: {bg_gradient};
            background-attachment: fixed;
        }}
        
        .main-header, .metric-card, .task-item {{
            background: {card_bg};
            padding: 1rem;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .task-item {{
            border-left: 4px solid {border_color};
            margin: 0.5rem 0;
            text-align: left;
        }}
        
        /* Set all general text elements to the theme color */
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, 
        .stSelectbox label, .stTextInput label, .stDateInput label, .stTextArea label {{
            color: {text_color} !important;
        }}
        
        /* Ensure metric labels and values are correct */
        .metric-label, .metric-value, .stMetric > div > div > div {{
             color: {text_color} !important;
        }}
        
        /* Input backgrounds for readability */
        .stTextInput > div > input, .stTextArea > div > textarea, .stSelectbox > div > div, 
        .stDateInput > div > input {{
            background: rgba(255, 255, 255, 0.9) !important;
            color: #333 !important; /* Text in inputs stays dark for contrast */
        }}
        
        /* Sidebar styling */
        .css-1d391kg, .sidebar .sidebar-content {{
            background: rgba(255, 255, 255, 0.8) !important; /* Keep sidebar light for now */
        }}
        
        /* Force black text in dataframes and tables */
        .dataframe, .dataframe td, .dataframe th {{
            color: black !important;
        }}
    </style>
    '''
    st.markdown(page_style, unsafe_allow_html=True)

# Initialize managers in session state
if 'task_manager' not in st.session_state:
    st.session_state.task_manager = TaskManager()
if 'goal_manager' not in st.session_state:
    st.session_state.goal_manager = GoalManager()

task_manager = st.session_state.task_manager
goal_manager = st.session_state.goal_manager

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = "Default"
    
# --- Call the style function with the current theme ---
set_page_style(st.session_state.theme) 
# ----------------------------------------------------

# Header
st.markdown('<div class="main-header"><h1>🚀 AI Career Tracker</h1><p>Track your progress, achieve your goals</p></div>', unsafe_allow_html=True)

# Top navigation
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
with col1:
    if st.button("📋 Tasks", use_container_width=True):
        st.session_state.page = "📋 Tasks"
with col2:
    if st.button("🎯 Goals", use_container_width=True):
        st.session_state.page = "🎯 Goals"
with col3:
    if st.button("📈 Analytics", use_container_width=True):
        st.session_state.page = "📈 Analytics"
with col4:
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.page = "⚙️ Settings"

# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = "📋 Tasks"

page = st.session_state.page

st.markdown("---")

if page == "📋 Tasks":
    # Task management section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📌 Add New Task")
        with st.form("task_form", clear_on_submit=True):
            col_date, col_cat = st.columns(2)
            with col_date:
                task_date = st.date_input("Date", value=date.today())
            with col_cat:
                category = st.selectbox("Category", 
                    ["Daily", "Weekly", "Monthly", "Learning", "Project", "Workout", "Networking", "Class"])
            
            task_text = st.text_input("Task Description", placeholder="What do you want to accomplish?")
            submitted = st.form_submit_button("➕ Add Task", use_container_width=True)
            
            if submitted:
                success, message = task_manager.add_task(task_date, category, task_text)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    with col2:
        # Quick stats for today only
        df = task_manager.load_tasks()
        today_tasks = df[df["date"].dt.date == date.today()] if not df.empty else pd.DataFrame()
        
        today_total = len(today_tasks)
        today_completed = today_tasks["completed"].sum() if not today_tasks.empty else 0
        today_completion_rate = (today_completed / today_total * 100) if today_total > 0 else 0
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Today's Tasks", today_total)
        st.metric("Completed Today", f'{today_completed} ({today_completion_rate:.1f}%)')
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Task display with date filter
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Today's Tasks")
    with col2:
        view_date = st.date_input("View Date", value=date.today(), key="view_date")
    
    # Load and filter tasks
    df = task_manager.load_tasks()
    if not df.empty:
        # Note: .dt.date comparison is key here
        filtered_tasks = df[df["date"].dt.date == view_date]
        
        if filtered_tasks.empty:
            st.info("No tasks for this date. Add some tasks above! 📝")
        else:
            # Display tasks with better UI
            for idx, row in filtered_tasks.iterrows():
                
                # CRITICAL FIX: Use the stable unique ID from the row
                task_id = row['id'] 
                col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
                
                with col1:
                    # Use task_id for the stable key
                    checked = st.checkbox("", value=row["completed"], key=f"task_{task_id}")
                    if checked != row["completed"]:
                        # Pass the task_id to the manager
                        task_manager.update_task(task_id, "completed", checked)
                        st.rerun()
                
                with col2:
                    status = "✅" if row["completed"] else "⏳"
                    st.markdown(f'{status} **[{row["category"]}]** {row["task"]}')
                
                with col3:
                    if st.button("🗑️", key=f"delete_{task_id}", help="Delete task"):
                        # Pass the task_id to the manager
                        task_manager.delete_task(task_id)
                        st.rerun()

elif page == "🎯 Goals":
    # Goals section (using GoalManager)
    st.subheader("🎯 Goals Management")
    
    goals_df = goal_manager.load_goals()
    summary = goal_manager.get_goal_summary()
    
    # Goals overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Goals", summary['total'])
    with col2:
        st.metric("Completed", summary['completed'])
    with col3:
        st.metric("In Progress", summary['in_progress'])
    with col4:
        st.metric("Not Started", summary['not_started'])
    
    # Add new goal
    with st.expander("➕ Add New Goal"):
        with st.form("add_goal_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Goal Title")
                deadline = st.date_input("Deadline")
            with col2:
                description = st.text_area("Description", height=100)
            
            if st.form_submit_button("Add Goal"):
                if title:
                    # Uses GoalManager method
                    goal_manager.add_goal(title, description, deadline) 
                    st.success("Goal added! 🎉")
                    st.rerun()
    
    # Display goals
goals_df = goal_manager.load_goals() # Reload all goals just in case

if not goals_df.empty:
    
    # --- NEW: Filter out completed goals to make them disappear ---
    goals_to_display = goals_df[goals_df["status"] != "Completed"].copy()

    st.subheader("Your Active Goals") # Changed header for clarity
    
    if goals_to_display.empty:
        st.info("Congratulations! You have no active goals. Add a new one above! 🎉")
    else:
        # Iterate over the FILTERED list (goals_to_display)
        for idx, row in goals_to_display.iterrows():
            # Use row['id'] for stable keys and updates
            goal_id = row['id'] 
            with st.expander(f"{row['title']} - {row['status']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Deadline:** {row['deadline'].strftime('%Y-%m-%d')}")
                with col2:
                    new_status = st.selectbox(
                        "Status:",
                        ["Not Started", "In Progress", "Completed"],
                        index=["Not Started", "In Progress", "Completed"].index(row["status"]),
                        key=f"status_{goal_id}" # Use the stable ID
                    )
                    if new_status != row["status"]:
                        # Uses GoalManager method to update
                        goal_manager.update_goal_status(goal_id, new_status) 
                        st.rerun()

elif page == "📈 Analytics":
    st.subheader("📈 Analytics Dashboard")
    
    # Load data
    df = task_manager.load_tasks()
    
    if not df.empty:
        # Task completion over time
        daily_completion = df.groupby(df['date'].dt.date).agg({
            'completed': ['count', 'sum']
        }).reset_index()
        daily_completion.columns = ['date', 'total_tasks', 'completed_tasks']
        daily_completion['completion_rate'] = (daily_completion['completed_tasks'] / daily_completion['total_tasks'] * 100).round(2)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Daily Completion Rate")
            fig = px.line(daily_completion, x='date', y='completion_rate', 
                         title="Daily Task Completion Rate (%)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Tasks by Category")
            category_counts = df['category'].value_counts()
            fig = px.pie(values=category_counts.values, names=category_counts.index,
                        title="Task Distribution by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        # Weekly trends
        st.subheader("📅 Weekly Overview")
        if len(daily_completion) >= 7:
            recent_week = daily_completion.tail(7)
            fig = go.Figure()
            
            # Use distinct colors for contrast
            fig.add_trace(go.Bar(x=recent_week['date'], y=recent_week['total_tasks'], 
                               name='Total Tasks', marker_color='#1f77b4'))
            fig.add_trace(go.Bar(x=recent_week['date'], y=recent_week['completed_tasks'], 
                               name='Completed Tasks', marker_color='#2ca02c'))
                               
            # CRITICAL CHART FIX: Use 'group' to place bars side-by-side
            fig.update_layout(title="Last 7 Days - Tasks Overview", barmode='group') 
            
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No data yet! Start adding tasks to see analytics. 📊")

elif page == "⚙️ Settings":
    st.subheader("⚙️ Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Data Management")
        
        # Export data
        if st.button("📤 Export Tasks"):
            df = task_manager.load_tasks()
            if not df.empty:
                csv = df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download Tasks CSV",
                    csv,
                    "tasks_backup.csv",
                    "text/csv"
                )
        
        # Data statistics
        st.subheader("📊 Data Overview")
        df = task_manager.load_tasks()
        goals_df = goal_manager.load_goals() # Uses GoalManager
        
        st.write(f"**Total Tasks:** {len(df)}")
        st.write(f"**Total Goals:** {len(goals_df)}")
        
        if not df.empty:
            st.write(f"**Date Range:** {df['date'].min().date()} to {df['date'].max().date()}")
    
    with col2:
        st.subheader("🎨 Customization")
        
        # --- THEME FIX: Save selection to session state and rerun ---
        new_theme = st.selectbox(
            "Theme", 
            ["Default", "Dark", "Light"], 
            index=["Default", "Dark", "Light"].index(st.session_state.theme),
            key="theme_selector"
        )
        
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun() # Rerun to apply the new style function
        # -----------------------------------------------------------
        
        # Category management
        st.subheader("📝 Categories")
        categories = ["Daily", "Weekly", "Monthly", "Learning", "Project", "Workout", "Networking", "Class"]
        selected_cats = st.multiselect("Active Categories", categories, default=categories)
        
        if st.button("💾 Save Settings"):
            # This save button now only handles other settings, theme is handled by st.rerun() above
            st.success("Settings saved! ⚙️")

df = task_manager.load_tasks()
if not df.empty:
    today_tasks = df[df["date"].dt.date == date.today()]
    total_today = len(today_tasks)
    completed_today = today_tasks["completed"].sum()
    
    st.sidebar.metric("Today's Progress", f"{completed_today}/{total_today}")
    
    if total_today > 0:
        progress = completed_today / total_today
        st.sidebar.progress(progress)
        
    # Show today's task categories
    if not today_tasks.empty:
        st.sidebar.subheader("📋 Today's Categories")
        category_counts = today_tasks['category'].value_counts()
        for cat, count in category_counts.items():
            st.sidebar.write(f"• {cat}: {count}")
else:
    st.sidebar.info("No tasks yet today!")
