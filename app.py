import streamlit as st
import sqlite3

# --- 1. DATABASE SETUP ---
# This creates a file called 'tasks.db' in your folder if it doesn't exist
conn = sqlite3.connect('tasks.db', check_same_thread=False)
cursor = conn.cursor()

# Create the table to hold our tasks
cursor.execute('''
    CREATE TABLE IF NOT EXISTS focus_tasks (
        id INTEGER PRIMARY KEY, 
        name TEXT, 
        completed BOOLEAN
    )
''')
conn.commit()

# If the database is brand new, create 3 empty slots
cursor.execute('SELECT COUNT(*) FROM focus_tasks')
if cursor.fetchone()[0] == 0:
    for _ in range(3):
        cursor.execute('INSERT INTO focus_tasks (name, completed) VALUES ("", 0)')
    conn.commit()


# --- 2. USER INTERFACE ---
st.set_page_config(page_title="Deep Work Dashboard", page_icon="🧠", layout="centered")
# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Change the main background color */
    .stApp {
        background-color: #f4f4f9; 
    }
    
    /* Style the main title */
    h1 {
        color: #2c3e50;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    
    /* Style the text inputs */
    .stTextInput > div > div > input {
        background-color: #fffff;
        color: #333333;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        padding: 10px;
    }
    
    /* Make the progress bar custom colors */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)
st.title("🧠 Deep Work Dashboard")
st.markdown("### Your Daily Top 3")
st.write("List the three most critical tasks you need to focus on today. They will save automatically.")

# Fetch the current saved tasks from the database
cursor.execute('SELECT id, name, completed FROM focus_tasks ORDER BY id LIMIT 3')
db_tasks = cursor.fetchall()

# Display the 3 focus slots
for i, (task_id, name, completed) in enumerate(db_tasks):
    col1, col2 = st.columns([0.1, 0.9])
    
    # Checkbox for completion
    is_checked = col1.checkbox("", key=f"check_{i}", value=bool(completed))
    
    # Text input for the task name
    new_name = col2.text_input(
        f"Task {i+1}", 
        value=name, 
        key=f"task_{i}", 
        label_visibility="collapsed",
        placeholder=f"Enter high-priority task {i+1}..."
    )
    
    # If the user typed a new name or clicked the checkbox, update the database
    if is_checked != bool(completed) or new_name != name:
        cursor.execute('''
            UPDATE focus_tasks 
            SET name = ?, completed = ? 
            WHERE id = ?
        ''', (new_name, int(is_checked), task_id))
        conn.commit()

# --- 3. PROGRESS TRACKING ---
st.divider()

# Fetch the freshest data to calculate the progress bar
cursor.execute('SELECT name, completed FROM focus_tasks')
current_tasks = cursor.fetchall()

# Filter out the empty slots
active_tasks = [t for t in current_tasks if t[0].strip() != ""]
completed_tasks = [t for t in active_tasks if t[1] == 1]

if active_tasks:
    progress = len(completed_tasks) / len(active_tasks)
    st.progress(progress)
    
    if progress == 1.0:
        st.success("🎉 All deep work targets achieved for today!")
    else:
        st.info(f"Keep going! {len(completed_tasks)} out of {len(active_tasks)} tasks completed.")
else:
    st.warning("Please enter at least one task to begin.")