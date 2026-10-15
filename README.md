# ⚡ StudySprint – Student Study Planner
> **Small steps. Big progress.**

StudySprint is a clean, focused, and beginner-friendly web application designed for high school and university students to plan study sessions, track subject assignments, and stay on top of critical deadlines without distractions.

*Built as a first GitHub portfolio project showcasing clean Python architecture, Streamlit state management, robust local persistence, and polished UI design for college opportunities and hackathons.*

---

## 📌 Problem Statement

Balancing coursework across STEM subjects (such as Mathematics, Programming, and Physics) often leaves students overwhelmed. Existing productivity tools are frequently overloaded with complex enterprise features, require paid subscriptions, mandate cloud logins, or fail to work offline. 

**StudySprint** addresses this problem by delivering a zero-friction, offline-capable study sprint planner. Students can quickly log upcoming study sessions, categorize by subject, assign realistic time estimates, and visually track their completion progress through an intuitive dashboard.

---

## ✨ Features

- **📊 Live Dashboard & Analytics:** Four dynamic metric cards showing *Total Tasks*, *Completed*, *Pending*, and *Overdue*, accompanied by an instant completion percentage progress bar with warm-yellow accent fill calculated directly from saved data.
- **➕ Structured Task Entry:** Quick-entry form with input validation:
  - Task Title (required, non-empty)
  - Subject (free-text input; defaults to "General" if left blank)
  - Due Date Picker
  - Estimated Study Duration in hours (enforced 0.5 to 12.0 hours)
  - Priority Level (*Low*, *Medium*, *High*)
- **🎯 Accurate Overdue Intelligence:** Automatically identifies overdue tasks based on local date comparison. A task due today is active and not overdue, while completed tasks are never marked overdue. Overdue tasks are highlighted with clear visual alert badges.
- **🔍 Instant Multi-View Filtering:** Filter your study sprint at any time by **All**, **Pending**, **Completed**, or **Overdue**.
- **⚡ Safe Task Actions:**
  - One-click toggle between *Mark Completed* and *Reopen Task*.
  - Protected deletion with a built-in confirmation safety checkbox to avoid accidental data loss.
- **🛡️ Bulletproof Local Persistence:** Tasks are stored in standard `tasks.csv`. If any rows are manually edited or corrupted, StudySprint gracefully skips bad rows with an informative warning banner instead of crashing or losing data.
- **🎨 Hackathon-Ready Design:** Styled in a soothing matcha-green palette: Deep Green (`#9DBF7C`), Light Green (`#C7DDAA`), Warm Yellow accent (`#FFF2A6`), Kiwi Cream background (`#E6F0C3`), and Muted Green (`#A7BC9A`), with clean rounded cards, dark readable text, and a responsive layout.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Frontend & App Framework:** [Streamlit](https://streamlit.io/) (v1.30+)
- **Storage:** Local CSV (`tasks.csv`) using Python's built-in `csv` module
- **Dependencies:** Exclusively `streamlit` (no external databases, third-party auth, or paid APIs required)

---

## 📁 Project Structure

```text
studysprint/
├── app.py              # Complete application code (modular, documented)
├── requirements.txt    # Python dependencies (contains only 'streamlit')
├── .gitignore          # Ignores .venv/, __pycache__/, and personal tasks.csv
└── README.md           # Comprehensive project guide and portfolio documentation
```

---

## 🚀 Windows Setup and Run Guide

Follow these simple steps in **VS Code** or **Windows PowerShell**:

### 1. Open the project folder in VS Code
Open VS Code, click **File > Open Folder...**, and select the `studysprint` folder.

### 2. Open a PowerShell terminal
Press ``Ctrl + ` `` (or select **Terminal > New Terminal** from the top menu).

### 3. Create and activate a Python virtual environment
```powershell
# Create a virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

> *Tip:* If PowerShell gives an execution policy warning when activating, run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> .\.venv\Scripts\Activate.ps1
> ```

### 4. Install dependencies
```powershell
pip install -r requirements.txt
```

### 5. Launch StudySprint
```powershell
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 💡 Example Usage Walkthrough

1. **Add your first sprint task:**
   - In the left panel (*Add New Task*), enter title: `Solve Problem Set 3`.
   - Type Subject: `Mathematics` (or type any course name, e.g., `Calculus II` or leave blank for `General`).
   - Select Priority: `High`.
   - Set Estimated Duration: `2.0` hours.
   - Click **Add Task to Sprint**.
2. **Track sprint metrics:**
   - Observe the top dashboard increment the **Total Tasks** and **Pending** counters.
3. **Filter and complete tasks:**
   - Click the **✓ Mark Completed** button once your study session finishes.
   - The completion progress bar will dynamically advance to show your updated completion percentage!
4. **Delete with safety check:**
   - To remove a task, tick the **Confirm** checkbox next to the task and press **🗑️ Delete**.

---

## 📸 Application Screenshot

```
+-----------------------------------------------------------------------------------+
|                                 ⚡ StudySprint                                    |
|                           Small steps. Big progress.                              |
+-----------------------------------------------------------------------------------+
|  [ 4 Total Tasks ]   |   [ 2 Completed ]   |   [ 1 Pending ]   |   [ 1 Overdue ]  |
|  Overall Progress: [=====================>           ] 50%                        |
+-----------------------------------------------------------------------------------+
| ➕ ADD NEW TASK                     | 📋 STUDY TASKS                              |
| Task Title: [                      ]| [● All] [Pending] [Completed] [Overdue]     |
| Subject: [ Mathematics v ]          | ------------------------------------------- |
| Priority: [ High v ]                | 📐 Solve Calculus Set 3                     |
| Due Date: [ 2026-10-16 ]            | ⚠️ OVERDUE | ● High Priority | ⏱️ 2.0 hrs    |
| Duration: [ 2.0 ] hours             | [✓ Mark Completed]  [ ] Confirm [🗑️ Delete]  |
| [ Add Task to Sprint ]              |                                             |
+-----------------------------------------------------------------------------------+
```
*(Replace with an actual screenshot image `![Dashboard](screenshot.png)` when preparing your repository demonstration)*

---

## 🔍 Limitations & Future Enhancements

### Current Prototype Limitations
- **Single-User Local Storage:** Tasks are saved in a local CSV file per computer rather than synced across multiple devices in the cloud.
- **Fixed Subject Categories:** Supports four core categories (*Mathematics*, *Programming*, *Physics*, *Other*).
- **Manual Time Tracking:** Relies on student estimates rather than an active countdown timer.

### Realistic Future Improvements
- **Pomodoro Study Timer:** Add an integrated 25-minute study timer with sound alerts right next to each task card.
- **Custom Subject Tags:** Allow students to create custom subjects with personalized color badges.
- **Export / Import Backup:** One-click download/upload of study sprint history in JSON or CSV format.
- **Weekly Study Analytics Chart:** Visual weekly graph of hours spent studying per subject using Streamlit charts.

---

## 🎓 About This Project

This project was built as a clean, practical beginner prototype for hackathons and undergraduate portfolio applications. It demonstrates fundamental software engineering principles: clean code separation, defensive input validation, atomic state handling in Streamlit, and persistent file I/O with error resilience.
