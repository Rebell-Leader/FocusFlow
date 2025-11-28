# 🦉 FocusFlow - AI Productivity Accountability Agent

**Your Duolingo-style AI buddy that keeps you focused while coding.**

[![Gradio](https://img.shields.io/badge/Built%20with-Gradio-orange)](https://gradio.app)
[![MCP](https://img.shields.io/badge/MCP-Enabled-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/MCP-1st-Birthday/FocusFlowAI)

## 🎯 The Problem

**"I'll just check Reddit for 5 minutes while wait for inspiration..." -> 3 hours later.**

Developers and creators often struggle with:
- **Task Paralysis**: Overwhelmed by big projects.
- **Context Switching**: Getting lost in unrelated rabbit holes.
- **Lack of Accountability**: No one to gently nudge you back to work.
- **"Busy" vs. Productive**: Doing work that doesn't actually move the needle.

## ✨ The Solution

**FocusFlow** is an AI-powered productivity partner that monitors your **actual work** (file changes, git commits) and gently nudges you when you drift off track. It's not a micromanager; it's a friendly companion that helps you maintain momentum.

1. **Breaks down projects** into 5-8 micro-tasks (15-30 min each)
2. **Monitors your workspace** in real-time (file changes or text input)
3. **Provides Duolingo-style nudges** when you get distracted or idle
4. **Tracks focus metrics** with streaks, scores, and visualizations
5. **Integrates with LLMs** via MCP (Model Context Protocol) for natural language task management
6. **Integrates with Linear MCP** for project management

## 🚀 Features

| Feature | Description |
| :--- | :--- |
| 🦉 **Duolingo-style Nudges** | Friendly, personality-driven reminders to stay on track. |
| 🔗 **MCP Integration** | Connects with tools like Claude Desktop for natural language task execution and  management. |
| 📋 **Linear Sync** | Import projects and tasks directly from Linear (via API). |
| 👁️ **Focus Monitoring** | Real-time file system monitoring to detect actual work. |
| 🛡️ **Privacy First** | Support for local LLMs (Ollama) or private API keys. |
| 🍅 **Pomodoro Timer** | Built-in timer with break reminders and audio alerts. |
| 📊 **Productivity Stats** | Track streaks, focus scores, and daily progress. |
| 🗣️ **Voice Feedback** | (Optional) ElevenLabs integration for spoken encouragement. |

## 🏗️ Architecture

```ascii
+----------------+      +------------------+      +----------------+
| Claude Desktop | <--> | FocusFlow (MCP)  | <--> | Linear API     |
| (MCP Client)   |      | (Gradio App)     |      | (Task Source)  |
+----------------+      +------------------+      +----------------+
       ^                        |
       |                        v
       |                +------------------+
       |                | Local File Sys   |
       |                | (Watchdog)       |
       |                +------------------+
       |                        |
       |                        v
+----------------+      +------------------+
| User Workspace | <--> | AI Agent Logic   |
| (Code/Docs)    |      | (LLM / Mock)     |
+----------------+      +------------------+
```

```
focusflow/
├── app.py              # Main Gradio application
├── agent.py            # AI focus agent (OpenAI/Anthropic/Mock)
├── storage.py          # Task manager with SQLite
├── monitor.py          # File monitoring with watchdog
├── metrics.py          # Productivity tracking
├── mcp_tools.py        # MCP tools and resources
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```


## ⚡ Quick Start

### 1. Installation

**Option A: Hugging Face Spaces (Try it now!)**
Click the "Try It" button above to run the demo version in your browser.

**Option B: Local Setup (Recommended for full features)**

```bash
# Clone the repository
git clone https://github.com/Rebell-Leader/FocusFlow.git
cd FocusFlow

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

### 2. Onboarding

1.  Open `http://localhost:5000`.
2.  **Home Tab**: Check your AI provider status.
3.  **Onboarding Tab**: Describe your project (e.g., "Build a React Native weather app") or import from Linear.
4.  **Task Manager**: See your decomposed micro-tasks.
5.  **Monitor**: Start working! FocusFlow will watch your file changes and update your status.

## 🛡️ Privacy & AI Providers

FocusFlow gives you full control over your data.

| Mode | Description | Best For |
| :--- | :--- | :--- |
| **Local (Ollama/vLLM)** | Runs 100% on your machine. No data leaves your network. | 🔒 Maximum Privacy |
| **Cloud (OpenAI/Anthropic/Gemini)** | Uses external APIs for smarter reasoning. | 🧠 Best Performance |
| **Mock AI** | Uses predefined responses. No API keys needed. | 🧪 Testing / Demos |

To configure, set `AI_PROVIDER` in your `.env` file (see below).

## 🔌 MCP Server Documentation

FocusFlow implements the **Model Context Protocol (MCP)**, allowing you to control it directly from Claude Desktop or other MCP clients.

### Connection Guide (Claude Desktop)

1.  **Prerequisite**: Ensure FocusFlow is running (`python app.py`).
2.  **Locate Config**:
    *   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
    *   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
3.  **Add Server**:

```json
{
  "mcpServers": {
    "focusflow": {
      "url": "http://<YOUR_LOCAL_IP>:5000/gradio_api/mcp"
    }
  }
}
*Note: If running on WSL, you may need to use the SSE endpoint URL instead.*
*Replace `<YOUR_LOCAL_IP>` with the IP address of your local machine or WSL (e.g., `172.x.x.x`).*

### Exposed Tools

| Tool | Signature | Description |
| :--- | :--- | :--- |
| `add_task` | `(title: str, description: str, duration: int)` | Create a new task. |
| `get_current_task` | `()` | Get the currently active task details. |
| `start_task` | `(task_id: int)` | Mark a task as 'In Progress'. |
| `mark_task_done` | `(task_id: int)` | Complete a task. |
| `get_all_tasks` | `()` | List all tasks and statuses. |
| `get_productivity_stats` | `()` | Get focus scores and streaks. |

### Exposed Resources

- `focusflow://tasks/all`: JSON list of all tasks.
- `focusflow://tasks/active`: JSON details of active task.
- `focusflow://stats`: Current productivity metrics.

### API Response Format

Tools return strings that are formatted for human/LLM reading, but resources return JSON.

**Example `get_current_task` response:**
```text
📋 Current Active Task:
- ID: 12
- Title: Implement Auth
- Status: In Progress
```

**Example `focusflow://tasks/active` resource:**
```json
{
  "id": 12,
  "title": "Implement Auth",
  "status": "In Progress",
  "estimated_duration": "30 min"
}
```

### Error Handling

All tools return descriptive error messages starting with `❌` if something goes wrong.

- **Task Not Found**: `❌ Task 99 not found. Use get_all_tasks() to see available tasks.`
- **Invalid Status**: `❌ Failed to start task. Task is already marked as Done.`
- **System Error**: `❌ Error creating task: [Error Details]`

### Example Usage (Claude)

> **User**: "What should I be working on?"
>
> **Claude**: (Calls `get_current_task`) "You are currently working on 'Implement Auth Middleware'. You've been focused for 15 minutes."

> **User**: "Add a task to fix the login bug."
>
> **Claude**: (Calls `add_task`) "Added 'Fix login bug' to your list."

## 📋 Linear Integration

FocusFlow integrates with Linear via their **GraphQL API** to sync your projects and tasks.

### Setup

1.  Get your **Linear API Key**: [https://linear.app/settings/api](https://linear.app/settings/api)
2.  Add it to your `.env` file: `LINEAR_API_KEY=lin_api_...`

### How it Works

1.  **Import**: In the "Onboarding" tab, FocusFlow fetches your Linear projects using `viewer { projects }`.
2.  **Sync**: It pulls active issues using `project { issues }`.
3.  **Create**: You can create new tasks in FocusFlow, which pushes them to Linear via `issueCreate`.

*(Screenshots of Linear import flow would go here)*

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure your preferences:

```bash
# .env example

# --- Launch Mode ---
# 'local': Monitors file system changes (Best for personal use)
# 'demo': Text-area simulation (Best for Hugging Face Spaces)
LAUNCH_MODE=local

# --- AI Provider ---
# Options: openai, anthropic, gemini, vllm, mock
AI_PROVIDER=anthropic

# --- API Keys ---
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LINEAR_API_KEY=lin_api_...

# --- MCP ---
ENABLE_MCP=true
```

## 🤝 Contributing

Contributions are welcome!
1.  Fork the repo.
2.  Create a feature branch.
3.  Submit a Pull Request.

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built for the [Gradio MCP Hackathon](https://gradio.app) - competing for **Track 1: Building MCP**
- Voice integration powered by [ElevenLabs](https://elevenlabs.io) - competing for **$2,000 Best Use of ElevenLabs** sponsor award
- Inspired by Duolingo's encouraging UX
- Uses [Model Context Protocol](https://modelcontextprotocol.io) for LLM integration

---
**Made with ❤️ for the Gradio MCP Hackathon.**
*Hoot hoot!* 🦉
