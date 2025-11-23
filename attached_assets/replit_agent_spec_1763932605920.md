# Technical Specification: FocusFlow AI Agent (Full Version)

## 1. Project Overview
**Name:** FocusFlow
**Goal:** Build an AI-powered "Accountability Buddy" that monitors a user's local coding workspace, tracks their progress against a task list, and provides "Duolingo-style" nudges (encouraging or sassy) to keep them focused.
**Target Platform:** Replit (Python) / Local Execution via Gradio 5.

## 2. Tech Stack
- **Frontend/UI:** Gradio 5.0+ (Must use `gradio[mcp]` capabilities).
- **Backend:** Python 3.11+.
- **AI/LLM:** OpenAI API (GPT-4o) or Anthropic API (Claude 3.5 Sonnet).
- **File Monitoring:** `watchdog` library for real-time file system events.
- **Data Storage:** SQLite or JSON-based local storage for Task CRUD.
- **Protocol:** Model Context Protocol (MCP) for the file monitor component.

## 3. Core Features & Architecture

### A. The "Onboarding" Agent
*   **Input:** A chat interface where the user describes their project (e.g., "I want to build a snake game in Python").
*   **Process:** The LLM analyzes the request and breaks it down into a structured list of "Micro-Tasks" (e.g., "Setup Pygame", "Draw Snake", "Handle Input").
*   **Output:** Populates the **Task Manager** with these tasks.

### B. Task Manager (CRUD)
*   **UI:** A clean list view in Gradio.
*   **Features:**
    *   Add/Edit/Delete tasks.
    *   Reorder tasks.
    *   Set "Active Task" (The single source of truth for the monitoring agent).
    *   **Fields:** ID, Title, Description, Status (Todo, In Progress, Done), Estimated Duration.

### C. The File Monitor (MCP Server)
*   **Role:** A custom MCP server implemented within the Gradio app.
*   **Function:** Watches a user-specified absolute directory path.
*   **Logic:**
    *   Detects file modifications, creations, and deletions.
    *   **Content-Awareness:** Reads the `diff` or the last 500 characters of modified text files.
    *   **Privacy:** Ignores `.git`, `__pycache__`, `.env`, and binary files.

### D. The Focus Agent (The "Brain")
*   **Loop:** Runs every 30-60 seconds.
*   **Input:**
    1.  Current "Active Task" (from Task Manager).
    2.  Recent File Activity (from File Monitor).
*   **Analysis (LLM):**
    *   Compares *Code Changes* vs *Task Description*.
    *   **Verdict:** "On Track", "Distracted", or "Idle".
*   **Intervention (The "Personality"):**
    *   **On Track:** "Great job! I see you added the movement logic."
    *   **Distracted:** "Wait, why are you editing `random_script.py`? We are building a Snake game! 🤨"
    *   **Idle:** "Files won't write themselves. *Hoot hoot.* 🦉"
*   **Alerts:** Triggers a browser alert (JS) or sound effect if "Distracted" or "Idle" persists.

## 4. User Flow (The "Happy Path")
1.  **Setup:** User launches app, enters OpenAI/Claude Key.
2.  **Onboarding:** User types: "Build a React To-Do App". Agent generates 5 tasks.
3.  **Selection:** User clicks "Start" on Task 1: "Initialize Project".
4.  **Work:** User edits files in VS Code (monitored folder).
5.  **Feedback:** Gradio UI updates in real-time with "✅ Working..." logs.
6.  **Distraction:** User starts browsing/editing unrelated files.
7.  **Nudge:** App plays a sound and shows a toast notification: "Eyes on the prize! 👀".

## 5. Implementation Guidelines
*   **Modular Code:** Separate `agent.py`, `monitor.py`, `storage.py`.
*   **Gradio 5 Features:** Use `gr.Timer` for the control loop. Use `gr.Browser` or custom JS for alerts.
*   **Error Handling:** Gracefully handle missing API keys or invalid paths.
