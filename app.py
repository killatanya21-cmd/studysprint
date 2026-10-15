"""
StudySprint - Student Study Planner
A lightweight, clean, and persistent study task manager built with Python and Streamlit.
"""

import csv
import os
import uuid
from datetime import date, datetime
import streamlit as st

# ==============================================================================
# CONSTANTS & CONFIGURATION
# ==============================================================================
CSV_FILE = "tasks.csv"
CSV_HEADERS = ["id", "title", "subject", "due_date", "duration", "priority", "status", "created_at"]

PRIORITY_OPTIONS = ["Low", "Medium", "High"]
STATUS_PENDING = "Pending"
STATUS_COMPLETED = "Completed"

# ==============================================================================
# DATA PERSISTENCE & VALIDATION
# ==============================================================================
def is_valid_date(date_str: str) -> bool:
    """Check if the string matches the required YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def is_overdue(task: dict, today: date) -> bool:
    """
    Overdue definition:
    - Status must be 'Pending'
    - Due date must be strictly before today's local date
    - A task due today is NOT overdue
    - Completed tasks are NEVER overdue
    """
    if task.get("status") != STATUS_PENDING:
        return False
    try:
        due_date = datetime.strptime(task.get("due_date", ""), "%Y-%m-%d").date()
        return due_date < today
    except (ValueError, TypeError):
        return False


def load_tasks_from_csv(filepath: str) -> tuple[list[dict], list[str]]:
    """
    Load tasks from CSV. Returns (valid_tasks, warning_messages).
    Skips corrupted rows safely without crashing or overwriting the file.
    Retains any existing subject values as-is.
    """
    valid_tasks = []
    warnings = []

    if not os.path.exists(filepath):
        # File doesn't exist yet; will be created on the first save
        return valid_tasks, warnings

    if os.path.getsize(filepath) == 0:
        # File is empty
        return valid_tasks, warnings

    try:
        with open(filepath, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            
            # Verify required columns exist in the header
            if not reader.fieldnames or not set(["id", "title", "due_date", "duration", "priority", "status"]).issubset(reader.fieldnames):
                warnings.append("CSV header is missing required columns. Starting with an empty session.")
                return valid_tasks, warnings

            for row_idx, row in enumerate(reader, start=2):
                task_id = (row.get("id") or "").strip()
                title = (row.get("title") or "").strip()
                subject = (row.get("subject") or "").strip() or "General"
                due_date_str = (row.get("due_date") or "").strip()
                duration_str = (row.get("duration") or "").strip()
                priority = (row.get("priority") or "").strip()
                status = (row.get("status") or "").strip()
                created_at = (row.get("created_at") or "").strip() or date.today().isoformat()

                # Row validation checks
                if not task_id:
                    warnings.append(f"Row {row_idx}: Skipped because Task ID is missing.")
                    continue
                if not title:
                    warnings.append(f"Row {row_idx}: Skipped because Task Title is empty.")
                    continue
                if not is_valid_date(due_date_str):
                    warnings.append(f"Row {row_idx}: Skipped because Due Date '{due_date_str}' is invalid (expected YYYY-MM-DD).")
                    continue
                try:
                    duration_val = float(duration_str)
                    if not (0.5 <= duration_val <= 12.0):
                        warnings.append(f"Row {row_idx}: Skipped because Duration {duration_val} is outside allowed range (0.5 to 12.0 hours).")
                        continue
                except (ValueError, TypeError):
                    warnings.append(f"Row {row_idx}: Skipped because Duration '{duration_str}' is not a valid number.")
                    continue

                if priority not in PRIORITY_OPTIONS:
                    warnings.append(f"Row {row_idx}: Skipped because Priority '{priority}' is invalid.")
                    continue
                if status not in [STATUS_PENDING, STATUS_COMPLETED]:
                    warnings.append(f"Row {row_idx}: Skipped because Status '{status}' is invalid.")
                    continue

                valid_tasks.append({
                    "id": task_id,
                    "title": title,
                    "subject": subject,
                    "due_date": due_date_str,
                    "duration": duration_val,
                    "priority": priority,
                    "status": status,
                    "created_at": created_at
                })
    except Exception as exc:
        warnings.append(f"Error reading tasks file: {exc}")

    return valid_tasks, warnings


def save_tasks_to_csv(tasks: list[dict], filepath: str) -> None:
    """Save the current task list to CSV using standard headers."""
    with open(filepath, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for task in tasks:
            writer.writerow({
                "id": task["id"],
                "title": task["title"],
                "subject": task.get("subject", "General"),
                "due_date": task["due_date"],
                "duration": task["duration"],
                "priority": task["priority"],
                "status": task["status"],
                "created_at": task.get("created_at", date.today().isoformat())
            })


# ==============================================================================
# STATE INITIALIZATION
# ==============================================================================
def init_session_state() -> None:
    """Load tasks into session_state once at startup to prevent rewrite loops on rerun."""
    if "tasks" not in st.session_state:
        tasks, warnings = load_tasks_from_csv(CSV_FILE)
        st.session_state.tasks = tasks
        st.session_state.corrupt_warnings = warnings

    if "flash_message" not in st.session_state:
        st.session_state.flash_message = None


# ==============================================================================
# TASK ACTIONS (Only these functions write to CSV and trigger a rerun)
# ==============================================================================
def handle_add_task(title: str, subject: str, due_date_val: date, duration: float, priority: str) -> bool:
    """Validate and add a new task, persist to CSV, and set a success notification."""
    cleaned_title = title.strip()
    if not cleaned_title:
        st.error("Task title cannot be empty. Please enter a meaningful title.")
        return False

    cleaned_subject = subject.strip() if subject else ""
    if not cleaned_subject:
        cleaned_subject = "General"

    if not (0.5 <= duration <= 12.0):
        st.error("Duration must be between 0.5 and 12.0 hours.")
        return False

    new_task = {
        "id": uuid.uuid4().hex[:8],
        "title": cleaned_title,
        "subject": cleaned_subject,
        "due_date": due_date_val.strftime("%Y-%m-%d"),
        "duration": float(duration),
        "priority": priority,
        "status": STATUS_PENDING,
        "created_at": date.today().isoformat()
    }

    st.session_state.tasks.append(new_task)
    save_tasks_to_csv(st.session_state.tasks, CSV_FILE)
    st.session_state.flash_message = f"Task '{cleaned_title}' added successfully!"
    st.rerun()
    return True


def handle_toggle_status(task_id: str) -> None:
    """Toggle a task between Pending and Completed, then persist to CSV."""
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            if task["status"] == STATUS_PENDING:
                task["status"] = STATUS_COMPLETED
                st.session_state.flash_message = f"Marked '{task['title']}' as completed! Great job!"
            else:
                task["status"] = STATUS_PENDING
                st.session_state.flash_message = f"Reopened task '{task['title']}'."
            break
    save_tasks_to_csv(st.session_state.tasks, CSV_FILE)
    st.rerun()


def handle_delete_task(task_id: str) -> None:
    """Delete a task by ID, persist to CSV, and clear confirmation flag."""
    task_to_delete = next((t for t in st.session_state.tasks if t["id"] == task_id), None)
    title = task_to_delete["title"] if task_to_delete else "Task"

    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]
    save_tasks_to_csv(st.session_state.tasks, CSV_FILE)
    st.session_state.flash_message = f"Deleted '{title}'."
    st.rerun()


# ==============================================================================
# UI STYLING & COMPONENTS (Soft Matcha-Green Palette)
# ==============================================================================
def apply_custom_styles() -> None:
    """
    Inject clean soft matcha-green styling:
    - Deep green (primary): #9DBF7C
    - Light green (secondary): #C7DDAA
    - Warm yellow (accent): #FFF2A6
    - Kiwi cream (page background): #E6F0C3
    - Muted green (supporting): #A7BC9A
    - Cards/inputs: #FFFFFF
    - Body text: Dark charcoal-green (#1F2E1B) for optimal contrast
    """
    st.markdown(
        """
        <style>
            /* App Page Background */
            .stApp {
                background-color: #E6F0C3 !important;
                color: #1F2E1B !important;
            }

            /* Container constraints */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 3.5rem;
                max-width: 1100px;
            }

            /* Header Section */
            .app-header {
                text-align: center;
                margin-bottom: 1.5rem;
                padding: 1.6rem 1rem;
                background-color: #FFFFFF;
                border: 2px solid #C7DDAA;
                border-radius: 16px;
                box-shadow: 0 3px 8px rgba(167, 188, 154, 0.22);
            }
            .app-title {
                color: #385C24;
                font-size: 2.3rem;
                font-weight: 800;
                margin-bottom: 0.2rem;
                letter-spacing: -0.5px;
            }
            .app-title-highlight {
                color: #9DBF7C;
            }
            .app-subtitle {
                color: #557A3F;
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 0;
            }

            /* Dashboard Metric Cards */
            .metric-card {
                background: #FFFFFF;
                border: 1.5px solid #C7DDAA;
                border-radius: 12px;
                padding: 1rem 1.1rem;
                text-align: center;
                box-shadow: 0 2px 6px rgba(167, 188, 154, 0.18);
            }
            .metric-num {
                font-size: 2.1rem;
                font-weight: 800;
                line-height: 1.2;
                margin-bottom: 0.2rem;
            }
            .metric-label {
                font-size: 0.85rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: #556B48;
            }
            .metric-total { color: #385C24; }
            .metric-completed { color: #2D6636; }
            .metric-pending { color: #8F5E0D; }
            .metric-overdue { color: #B91C1C; }

            /* Progress Bar Styling (Warm yellow #FFF2A6 fill) */
            div[data-testid="stProgressBar"] > div {
                background-color: #FFFFFF !important;
                border: 1px solid #C7DDAA !important;
                border-radius: 8px !important;
                height: 14px !important;
            }
            div[data-testid="stProgressBar"] > div > div {
                background-color: #FFF2A6 !important;
                border-radius: 6px !important;
            }
            div[data-testid="stProgress"] div[role="progressbar"] {
                background-color: #FFF2A6 !important;
            }

            /* Form Card Container */
            div[data-testid="stForm"] {
                background-color: #FFFFFF !important;
                border: 1.5px solid #C7DDAA !important;
                border-radius: 14px !important;
                padding: 1.4rem !important;
                box-shadow: 0 2px 6px rgba(167, 188, 154, 0.15) !important;
            }

            /* Task Card Container */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #FFFFFF !important;
                border: 1.5px solid #C7DDAA !important;
                border-radius: 12px !important;
                box-shadow: 0 2px 6px rgba(167, 188, 154, 0.15) !important;
                padding: 0.75rem 0.9rem !important;
                margin-bottom: 0.85rem !important;
            }

            /* Task Card Typography */
            .task-card-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: #1F2E1B;
                margin-bottom: 0.35rem;
                line-height: 1.3;
            }
            .task-title-done {
                color: #7A8E71 !important;
            }

            /* Badges Row */
            .badge-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin-bottom: 0.45rem;
            }
            .badge {
                display: inline-flex;
                align-items: center;
                padding: 0.22rem 0.6rem;
                font-size: 0.8rem;
                font-weight: 600;
                border-radius: 6px;
                line-height: 1.2;
            }
            .badge-subject {
                background-color: #F1F7E4;
                color: #2D4A22;
                border: 1px solid #C7DDAA;
            }
            .badge-prio-high {
                background-color: #FEE2E2;
                color: #991B1B;
                border: 1px solid #FCA5A5;
            }
            .badge-prio-medium {
                background-color: #FFF2A6;
                color: #735100;
                border: 1px solid #E5D57E;
            }
            .badge-prio-low {
                background-color: #E2EED7;
                color: #2D5322;
                border: 1px solid #C7DDAA;
            }
            .badge-overdue {
                background-color: #FEE2E2;
                color: #991B1B;
                font-weight: 700;
                border: 1.5px solid #EF4444;
            }
            .badge-completed {
                background-color: #C7DDAA;
                color: #1F3B1A;
                font-weight: 700;
                border: 1px solid #A7BC9A;
            }

            /* Metadata Row */
            .task-meta-row {
                font-size: 0.88rem;
                color: #374E30;
                margin-bottom: 0.65rem;
            }
            .task-meta-row strong {
                color: #1F2E1B;
            }

            /* Inputs & Selects: White and Readable */
            input, select, textarea {
                background-color: #FFFFFF !important;
                color: #1F2E1B !important;
                border: 1px solid #C7DDAA !important;
                border-radius: 8px !important;
            }
            input:focus, select:focus, textarea:focus {
                border-color: #9DBF7C !important;
                box-shadow: 0 0 0 1px #9DBF7C !important;
            }

            /* Buttons */
            .stFormSubmitButton > button {
                background-color: #9DBF7C !important;
                color: #1F2E1B !important;
                font-weight: 700 !important;
                border: 1px solid #8EA76F !important;
                border-radius: 8px !important;
                transition: background-color 0.15s ease;
            }
            .stFormSubmitButton > button:hover {
                background-color: #C7DDAA !important;
                border-color: #9DBF7C !important;
            }

            /* Regular Action Buttons */
            .stButton > button {
                border-radius: 8px !important;
                border: 1px solid #C7DDAA !important;
                background-color: #FFFFFF !important;
                color: #1F2E1B !important;
                font-weight: 600 !important;
            }
            .stButton > button:hover {
                background-color: #E6F0C3 !important;
                border-color: #9DBF7C !important;
            }

            /* Filter Bar Container */
            div[data-testid="stRadio"] > div {
                background-color: #FFFFFF !important;
                padding: 6px 12px !important;
                border-radius: 10px !important;
                border: 1.5px solid #C7DDAA !important;
            }
            div[data-testid="stRadio"] label {
                color: #1F2E1B !important;
                font-weight: 600 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render the application header with title and motto."""
    st.markdown(
        """
        <div class="app-header">
            <div class="app-title">⚡ <span class="app-title-highlight">Study</span>Sprint</div>
            <div class="app-subtitle">Small steps. Big progress.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(tasks: list[dict], today: date) -> None:
    """Compute and display summary cards and the warm-yellow progress bar."""
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.get("status") == STATUS_COMPLETED)
    pending_tasks = sum(1 for t in tasks if t.get("status") == STATUS_PENDING)
    overdue_tasks = sum(1 for t in tasks if is_overdue(t, today))

    # Metric Cards Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-num metric-total">{total_tasks}</div>
                <div class="metric-label">Total Tasks</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-num metric-completed">{completed_tasks}</div>
                <div class="metric-label">Completed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-num metric-pending">{pending_tasks}</div>
                <div class="metric-label">Pending</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-num metric-overdue">{overdue_tasks}</div>
                <div class="metric-label">Overdue</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    # Progress Bar with Warm Yellow fill
    if total_tasks > 0:
        percent = int((completed_tasks / total_tasks) * 100)
        st.progress(completed_tasks / total_tasks)
        st.caption(f"**Overall Progress:** {percent}% completed ({completed_tasks} of {total_tasks} tasks done)")
    else:
        st.progress(0.0)
        st.caption("**Overall Progress:** 0% (No tasks recorded yet)")


def render_add_task_form() -> None:
    """Form to capture a new study task with free-text subject and clean inputs."""
    st.subheader("➕ Add New Task")
    with st.form(key="add_task_form", clear_on_submit=True):
        title = st.text_input("Task Title*", placeholder="e.g., Solve Problem Set 3")

        col_subj, col_prio = st.columns(2)
        with col_subj:
            # Replaced dropdown with free text input
            subject = st.text_input("Subject", placeholder="Type your subject (e.g., Mathematics)")
        with col_prio:
            priority = st.selectbox("Priority", PRIORITY_OPTIONS, index=1)

        col_date, col_dur = st.columns(2)
        with col_date:
            due_date_val = st.date_input("Due Date", value=date.today())
        with col_dur:
            duration = st.number_input(
                "Estimated Duration (hours)",
                min_value=0.5,
                max_value=12.0,
                value=1.5,
                step=0.5,
                help="Enter estimated study time between 0.5 and 12 hours"
            )

        submit_btn = st.form_submit_button("Add Task to Sprint", use_container_width=True)
        if submit_btn:
            handle_add_task(title, subject, due_date_val, duration, priority)


def render_task_card(task: dict, today: date) -> None:
    """
    Render an individual task card as one compact, tidy card:
    - Title on top
    - Row with subject and priority badges (and overdue/completed indicators)
    - Row with due date and duration
    - Action buttons: Complete/Reopen and Delete with Confirmation
    """
    task_id = task["id"]
    is_done = task.get("status") == STATUS_COMPLETED
    overdue = is_overdue(task, today)

    prio = task.get("priority", "Medium")
    prio_class = f"badge-prio-{prio.lower()}"

    with st.container(border=True):
        # 1. Title on top (using native Markdown, never showing literal HTML tags)
        if is_done:
            st.markdown(f"#### ~~{task['title']}~~")
        else:
            st.markdown(f"#### {task['title']}")

        # 2. Row with subject and priority badges, plus overdue and completed chips
        badges = [
            f"<span class='badge badge-subject'>📚 {task['subject']}</span>",
            f"<span class='badge {prio_class}'>● {prio} Priority</span>"
        ]
        if overdue:
            badges.append("<span class='badge badge-overdue'>⚠️ OVERDUE</span>")
        if is_done:
            badges.append("<span class='badge badge-completed'>✓ Completed</span>")

        # Zero indentation ensures Markdown parser does not treat this as code
        st.markdown(" ".join(badges), unsafe_allow_html=True)

        # 3. Row with due date and duration
        overdue_note = " :red[**(Past Due)**]" if overdue else ""
        dur_unit = "hr" if task["duration"] == 1.0 else "hrs"
        st.markdown(f"📅 **Due:** {task['due_date']}{overdue_note}  •  ⏱️ **Estimated:** {task['duration']} {dur_unit}")

        # 4. Action buttons: Complete/Reopen and Delete with Confirmation
        btn_col1, btn_col2 = st.columns([1, 1])

        with btn_col1:
            if is_done:
                if st.button("↺ Reopen Task", key=f"reopen_{task_id}", use_container_width=True):
                    handle_toggle_status(task_id)
            else:
                if st.button("✓ Mark Completed", key=f"complete_{task_id}", use_container_width=True):
                    handle_toggle_status(task_id)

        with btn_col2:
            confirm_key = f"chk_del_{task_id}"
            col_chk, col_del = st.columns([1, 1.2])
            with col_chk:
                confirm = st.checkbox("Confirm", key=confirm_key, help="Check to enable deletion")
            with col_del:
                if st.button("🗑️ Delete", key=f"del_{task_id}", disabled=not confirm, use_container_width=True):
                    handle_delete_task(task_id)


def render_task_list(tasks: list[dict], today: date) -> None:
    """Filter, sort, and display tasks with clean empty states."""
    st.subheader("📋 Study Tasks")

    # Filter selector
    filter_choice = st.radio(
        "Filter by Status",
        options=["All", "Pending", "Completed", "Overdue"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # Filter logic
    if filter_choice == "Pending":
        displayed_tasks = [t for t in tasks if t.get("status") == STATUS_PENDING]
    elif filter_choice == "Completed":
        displayed_tasks = [t for t in tasks if t.get("status") == STATUS_COMPLETED]
    elif filter_choice == "Overdue":
        displayed_tasks = [t for t in tasks if is_overdue(t, today)]
    else:
        displayed_tasks = tasks

    # Empty states
    if not tasks:
        st.info("🌱 **Your sprint is clean!** No study tasks yet. Use the form on the left to add your first goal.")
        return

    if not displayed_tasks:
        st.info(f"No tasks found matching filter: **{filter_choice}**.")
        return

    # Render filtered tasks as compact, tidy cards
    for task in displayed_tasks:
        render_task_card(task, today)


# ==============================================================================
# MAIN APPLICATION ENTRY POINT
# ==============================================================================
def main() -> None:
    """Configure page, initialize state, and render UI layout."""
    st.set_page_config(
        page_title="StudySprint – Student Study Planner",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    apply_custom_styles()
    init_session_state()

    today = date.today()

    render_header()

    # Flash notification message
    if st.session_state.flash_message:
        st.success(st.session_state.flash_message)
        st.session_state.flash_message = None

    # Corrupt CSV warning notice (if any malformed rows were skipped)
    if st.session_state.corrupt_warnings:
        with st.expander("⚠️ Warnings during CSV file loading (Skipped Corrupt Rows)", expanded=False):
            for msg in st.session_state.corrupt_warnings:
                st.warning(msg)

    # Top Dashboard Stats
    render_dashboard(st.session_state.tasks, today)
    st.divider()

    # Responsive 2-Column Layout: Add Form on Left, Tasks on Right
    col_form, col_tasks = st.columns([1, 1.4], gap="large")

    with col_form:
        render_add_task_form()

    with col_tasks:
        render_task_list(st.session_state.tasks, today)


if __name__ == "__main__":
    main()
