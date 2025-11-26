# 🦉 FocusFlow - AI Productivity Accountability Agent

**Your Duolingo-style AI buddy that keeps you focused while coding**

[![Gradio](https://img.shields.io/badge/Built%20with-Gradio-orange)](https://gradio.app)
[![MCP](https://img.shields.io/badge/MCP-Enabled-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)

## 🎯 The Problem

Developers with ADHD and procrastination tendencies struggle with:
- **Task paralysis**: Breaking projects into manageable pieces
- **Context switching**: Getting distracted by unrelated files/tasks
- **Accountability**: No one keeping them on track during work sessions
- **Progress tracking**: Not knowing if they're making real progress

## ✨ The Solution

FocusFlow is an AI-powered productivity partner that:
1. **Breaks down projects** into 5-8 micro-tasks (15-30 min each)
2. **Monitors your workspace** in real-time (file changes or text input)
3. **Provides Duolingo-style nudges** when you get distracted or idle
4. **Tracks focus metrics** with streaks, scores, and visualizations
5. **Integrates with LLMs** via MCP (Model Context Protocol) for natural language task management

## 🚀 Key Features

### 🎯 AI-Powered Project Onboarding
- Describe your project in plain English
- Get actionable micro-tasks instantly
- Smart task generation based on project type (web, API, etc.)

### 👁️ Real-Time Focus Monitoring
- **Local Mode**: Watches your project directory for file changes
- **Demo Mode**: Simulates workspace with text area (perfect for HuggingFace Spaces)
- Content-aware analysis (reads code changes, not just filenames)

### 🦉 Duolingo-Style Personality
- **On Track**: "Great work! You're making solid progress! 🎯"
- **Distracted**: "Wait, what are you working on? That doesn't look like the task! 🤨"
- **Idle**: "Files won't write themselves. *Hoot hoot.* 🦉"

### 📊 Productivity Dashboard
- **Focus Score**: 0-100 rating based on on-track percentage
- **Streaks**: Consecutive "On Track" checks 🔥
- **Weekly Trends**: Visualize your focus patterns
- **State Distribution**: See where your time goes

### 🍅 Built-in Pomodoro Timer
- 25-minute work sessions
- 5-minute break reminders
- Audio alerts + browser notifications
- Auto-switching between work and break modes

### 🔗 MCP Integration (Game Changer!)
Connect FocusFlow to Claude Desktop, Cursor, or any MCP-compatible client!

**Available MCP Tools:**
- `add_task(title, description, duration)` - Create tasks via conversation
- `get_current_task()` - Check what you should be working on
- `start_task(task_id)` - Begin a focus session
- `mark_task_done(task_id)` - Complete tasks
- `get_all_tasks()` - List all tasks
- `get_productivity_stats()` - View your metrics

**MCP Resources:**
- `focusflow://tasks/all` - Full task list
- `focusflow://tasks/active` - Current active task
- `focusflow://stats` - Productivity statistics

## 📦 Installation

### Quick Start (Demo Mode)

```bash
# Clone the repository
git clone https://github.com/yourusername/focusflow.git
cd focusflow

# Install dependencies
pip install -r requirements.txt

# Run in demo mode (no API keys needed!)
python app.py
```

Open `http://localhost:5000` in your browser.

### With AI Provider (Optional)

FocusFlow supports multiple AI providers:

```bash
# Option 1: OpenAI
export AI_PROVIDER=openai
export OPENAI_API_KEY=your_key_here

# Option 2: Anthropic Claude
export AI_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your_key_here

# Option 3: vLLM (local inference)
export AI_PROVIDER=vllm
export VLLM_BASE_URL=http://localhost:8000/v1
export VLLM_MODEL=ibm-granite/granite-4.0-h-1b

# Then run
python app.py
```

**No API keys? No problem!** FocusFlow automatically uses a **Mock AI** agent with predefined responses for testing.

### For Hackathon Organizers (HuggingFace Spaces)

To enable AI features on demo deployments, set **demo API keys** as environment variables:

```bash
DEMO_ANTHROPIC_API_KEY=sk-ant-xxx  # Checked first, falls back to user keys
DEMO_OPENAI_API_KEY=sk-xxx         # Same fallback logic
```

If demo keys run out of credits, FocusFlow gracefully falls back to Mock AI mode automatically.

## 🔌 Connecting to Claude Desktop (MCP)

### Step 1: Start FocusFlow

```bash
python app.py
```

You'll see:
```
🔗 MCP Server enabled! Connect via Claude Desktop or other MCP clients.
* Streamable HTTP URL: http://localhost:5000/gradio_api/mcp/
```

### Step 2: Configure Claude Desktop

#### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "focusflow": {
      "command": "python",
      "args": ["/absolute/path/to/your/focusflow/app.py"]
    }
  }
}
```

#### Windows
Edit `%APPDATA%\Claude\claude_desktop_config.json` with the same JSON format.

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. You should see FocusFlow tools available!

### Step 4: Test It Out

In Claude Desktop, try:
```
"Add a task to build a REST API with authentication"
"What task should I work on now?"
"Mark task 1 as done"
"Show me my productivity stats"
```

## ⚙️ Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LAUNCH_MODE` | `demo` | `demo` (text area) or `local` (file monitoring) |
| `AI_PROVIDER` | `openai` | `openai`, `anthropic`, `vllm`, or `mock` |
| `MONITOR_INTERVAL` | `30` | Seconds between focus checks |
| `ENABLE_MCP` | `true` | Enable/disable MCP server |
| `OPENAI_API_KEY` | - | OpenAI API key (if using OpenAI) |
| `ANTHROPIC_API_KEY` | - | Anthropic API key (if using Claude) |
| `VLLM_BASE_URL` | `http://localhost:8000/v1` | vLLM server URL |
| `VLLM_MODEL` | `ibm-granite/granite-4.0-h-1b` | vLLM model name |

## 📁 Project Structure

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

## 🎥 Demo & Screenshots

### Home Screen
Clean interface with feature overview and configuration status.

### Onboarding
AI generates micro-tasks from project descriptions.

### Task Manager
Kanban-style task board with drag-and-drop (coming soon).

### Dashboard
Visualize focus scores, streaks, and productivity trends.

### Monitor
Real-time focus checks with Duolingo-style feedback.

## 🏆 Why This is Perfect for the Gradio MCP Hackathon

1. **Novel MCP Use Case**: First MCP-powered productivity/accountability tool
2. **Deep Integration**: Natural language task management through Claude Desktop
3. **Real Problem**: Solves actual pain points for developers with ADHD
4. **Gradio Showcase**: Uses tabs, plots, timers, state management, custom JS
5. **Demo-Friendly**: Works without API keys, deployable to HF Spaces
6. **Production-Ready**: SQLite persistence, metrics tracking, error handling

## 🚀 Deployment

### HuggingFace Spaces

1. Create a new Gradio Space
2. Upload all files
3. Set environment variables in Space settings:
   ```
   LAUNCH_MODE=demo
   AI_PROVIDER=openai
   OPENAI_API_KEY=your_key_here
   ```
4. Done! Your MCP server will be accessible at `https://yourspace.hf.space/gradio_api/mcp/`

### Replit

1. Import this repository
2. Set secrets in Replit Secrets
3. Run `python app.py`
4. Share the Replit URL

## 🛠️ Tech Stack

- **Frontend**: Gradio 5.0+ (Python UI framework)
- **Backend**: Python 3.11+
- **Database**: SQLite (zero-config persistence)
- **AI Providers**: OpenAI GPT-4, Anthropic Claude, vLLM, or Mock
- **File Monitoring**: Watchdog (real-time filesystem events)
- **MCP Integration**: Model Context Protocol for LLM interoperability
- **Charts**: Gradio native plots (pandas DataFrames)

## 📈 Roadmap

- [ ] Mobile app (React Native + Gradio backend)
- [ ] GitHub integration (auto-detect tasks from issues)
- [ ] Slack/Discord notifications
- [ ] Team mode (shared accountability)
- [ ] Voice commands (Whisper integration)
- [ ] VS Code extension

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this for personal or commercial projects!

## 🙏 Acknowledgments

- Built for the [Gradio MCP Hackathon](https://gradio.app)
- Inspired by Duolingo's encouraging UX
- Uses [Model Context Protocol](https://modelcontextprotocol.io) for LLM integration

---

**Made with ❤️ for developers with ADHD who just need a little nudge to stay focused.**

*Hoot hoot!* 🦉
