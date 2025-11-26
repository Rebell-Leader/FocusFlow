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

# Option 3: Google Gemini
export AI_PROVIDER=gemini
export GEMINI_API_KEY=your_key_here

# Option 4: vLLM (local inference)
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
DEMO_GEMINI_API_KEY=xxx            # Same fallback logic
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

## 🆕 Recent Updates

### Version 1.0 (Hackathon Release)
- ✅ **MCP Integration** - Full Model Context Protocol support with 8 tools and 3 resources
- ✅ **Voice Feedback** - ElevenLabs integration for Duolingo-style audio nudges
- ✅ **Demo API Keys** - Support for `DEMO_ANTHROPIC_API_KEY`, `DEMO_OPENAI_API_KEY`, and `DEMO_ELEVEN_API_KEY` for hackathon deployments
- ✅ **Productivity Dashboard** - Focus scores, streaks, weekly trends, and state distribution charts
- ✅ **Mock AI Mode** - Works without API keys for testing and demos
- ✅ **Graceful Degradation** - Automatically falls back to Mock AI if API keys are invalid or out of credits
- ✅ **Dual Launch Modes** - Demo mode (text area) and Local mode (file monitoring)
- ✅ **Comprehensive Testing** - Full testing checklist in `TESTING_CHECKLIST.md`
- ✅ **Error Handling** - Invalid task IDs return helpful error messages in MCP tools
- ✅ **Metrics Integration** - MCP `get_productivity_stats()` includes focus scores and streaks

## ⚙️ Configuration & Environment Variables

### Core Settings

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `LAUNCH_MODE` | `demo` | `demo`, `local` | Workspace monitoring mode (see Launch Modes below) |
| `AI_PROVIDER` | `anthropic` | `openai`, `anthropic`, `vllm`, `mock` | AI provider to use |
| `MONITOR_INTERVAL` | `30` | Any integer | Seconds between automatic focus checks |
| `ENABLE_MCP` | `true` | `true`, `false` | Enable/disable MCP server |

### AI Provider API Keys

**Priority Order:** Demo keys are checked first, then user keys, then falls back to Mock AI.

#### User API Keys
| Variable | Description | Get Key From |
|----------|-------------|--------------|
| `OPENAI_API_KEY` | Your personal OpenAI API key | https://platform.openai.com/api-keys |
| `ANTHROPIC_API_KEY` | Your personal Anthropic API key | https://console.anthropic.com/ |
| `ELEVEN_API_KEY` | Your personal ElevenLabs API key (optional) | https://elevenlabs.io/api |

#### Demo API Keys (For Hackathon Organizers)
| Variable | Description | Use Case |
|----------|-------------|----------|
| `DEMO_ANTHROPIC_API_KEY` | Shared Anthropic key for demos | Set on HuggingFace Spaces for judges/testers |
| `DEMO_OPENAI_API_KEY` | Shared OpenAI key for demos | Set on HuggingFace Spaces for judges/testers |
| `DEMO_ELEVEN_API_KEY` | Shared ElevenLabs key for voice | Set on HuggingFace Spaces for voice feedback |

**How It Works:**
```python
# Priority chain (Anthropic example):
1. Check DEMO_ANTHROPIC_API_KEY (hackathon demo key)
2. If not found, check ANTHROPIC_API_KEY (user's personal key)
3. If not found or invalid, fall back to Mock AI (no errors!)

# Voice integration (optional):
1. Check DEMO_ELEVEN_API_KEY (hackathon demo key)
2. If not found, check ELEVEN_API_KEY (user's personal key)
3. If not found, gracefully disable voice (text-only mode)
```

#### vLLM Settings (Local Inference)
| Variable | Default | Description |
|----------|---------|-------------|
| `VLLM_BASE_URL` | `http://localhost:8000/v1` | vLLM server endpoint |
| `VLLM_MODEL` | `ibm-granite/granite-4.0-h-1b` | Model name |
| `VLLM_API_KEY` | `EMPTY` | API key (usually not needed for local) |

### API Key Management Best Practices

**For Local Development:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your personal keys
nano .env  # or your preferred editor
```

**For HuggingFace Spaces Deployment:**
```bash
# In Space Settings > Variables, add:
LAUNCH_MODE=demo
AI_PROVIDER=anthropic
DEMO_ANTHROPIC_API_KEY=sk-ant-your-hackathon-key
```

**For Testing Without API Keys:**
```bash
# Just run - Mock AI activates automatically!
python app.py
# Status: "ℹ️ Running in DEMO MODE with Mock AI (no API keys needed). Perfect for testing! 🎭"
```

### Graceful Degradation

FocusFlow **never crashes** due to missing or invalid API keys:

| Scenario | Behavior | User Experience |
|----------|----------|-----------------|
| No API keys set | Uses Mock AI | ✅ Full demo functionality |
| Invalid API key | Falls back to Mock AI | ✅ App continues working |
| API out of credits | Falls back to Mock AI | ✅ Seamless transition |
| API rate limited | Retries, then Mock AI | ✅ No interruption |

**Status Messages:**
- `✅ Anthropic Claude initialized successfully (demo key)` - Demo key working
- `✅ OpenAI GPT-4 initialized successfully (user key)` - User key working
- `ℹ️ Running in DEMO MODE with Mock AI (no API keys needed)` - Fallback active

## 🎮 Launch Modes Explained

FocusFlow supports two workspace monitoring modes:

### Demo Mode (`LAUNCH_MODE=demo`)

**Best for:**
- HuggingFace Spaces deployments
- Replit deployments
- Testing without file system access
- Hackathon demos for judges

**How it works:**
- Provides a text area for simulating workspace activity
- Users type what they're working on
- AI analyzes text content for focus checks
- No file system permissions needed

**Example:**
```bash
export LAUNCH_MODE=demo
python app.py
# Monitor tab shows: "Demo Workspace" text area
```

**User Workflow:**
1. Type: "Working on authentication API, creating login endpoint"
2. Click "Check Focus Now"
3. Result: "On Track! Great work! 🎯"

### Local Mode (`LAUNCH_MODE=local`)

**Best for:**
- Local development environments
- Real-time file monitoring
- Production use cases
- Personal productivity tracking

**How it works:**
- Uses `watchdog` library to monitor file system changes
- Automatically detects file modifications in project directory
- Reads actual file diffs for intelligent analysis
- Triggers focus checks automatically when files change

**Example:**
```bash
export LAUNCH_MODE=local
python app.py
# Monitor tab shows: "Watching directory: /your/project/path"
```

**User Workflow:**
1. Start a task in Task Manager
2. Edit files in your project
3. FocusFlow automatically detects changes and runs focus checks
4. Receive real-time feedback

### Choosing the Right Mode

| Use Case | Recommended Mode | Reason |
|----------|------------------|--------|
| HuggingFace Spaces | `demo` | No file system access in web deployments |
| Hackathon demo | `demo` | Easy for judges to test without setup |
| Local development | `local` | Real-time file monitoring is more natural |
| Replit | `demo` | Simpler, no file permissions issues |
| Personal productivity | `local` | Authentic workspace monitoring |

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

## 🧪 Testing

### Quick Feature Test (5 minutes)

Use the comprehensive **`TESTING_CHECKLIST.md`** file for detailed testing instructions. Here's a quick verification:

```bash
# 1. Start the app
python app.py

# 2. Open browser
open http://localhost:5000

# 3. Test each tab:
# ✅ Home: Check status message shows AI provider
# ✅ Onboarding: Generate tasks from project description
# ✅ Task Manager: Create/edit/delete/start tasks
# ✅ Monitor: Perform focus checks (demo workspace or file changes)
# ✅ Dashboard: View metrics after focus checks
# ✅ Pomodoro: Start/pause/reset timer
```

### Test Scenarios

**Scenario 1: Demo Mode (No API Keys)**
```bash
# No .env file needed
python app.py
# Expected: "ℹ️ Running in DEMO MODE with Mock AI"
# Test: All features work with predefined responses
```

**Scenario 2: With Anthropic API Key**
```bash
export AI_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-your-key
python app.py
# Expected: "✅ Anthropic Claude initialized successfully (user key)"
# Test: Intelligent task generation and focus analysis
```

**Scenario 3: Demo Key (Hackathon Deployment)**
```bash
export AI_PROVIDER=anthropic
export DEMO_ANTHROPIC_API_KEY=sk-ant-demo-key
python app.py
# Expected: "✅ Anthropic Claude initialized successfully (demo key)"
# Test: Uses demo key, falls back to Mock if exhausted
```

**Scenario 4: MCP Integration**
```bash
# 1. Configure Claude Desktop (see MCP section above)
# 2. Start FocusFlow
python app.py
# 3. In Claude Desktop, test tools:
#    - "Add a task to implement OAuth2"
#    - "What's my current task?"
#    - "Show my productivity stats"
```

### Automated Testing

Run the full test suite:
```bash
# Follow TESTING_CHECKLIST.md step-by-step
# Expected: All features pass without errors
# Time: ~15 minutes for comprehensive test
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "No API key" error | Set `AI_PROVIDER=mock` or leave keys empty - Mock AI activates automatically |
| Charts show "Infinite extent" warning | Normal on first load with no data - warnings disappear after focus checks |
| MCP tools not visible in Claude | Restart Claude Desktop after config changes |
| File monitoring not working | Check `LAUNCH_MODE=local` and file permissions |
| Tasks not persisting | Check `focusflow.db` file exists and is writable |

## 🚀 Deployment

### Deployment Option 1: HuggingFace Spaces (Recommended for Hackathon)

**Step 1: Create Space**
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Select "Gradio" as SDK
4. Choose a name (e.g., `focusflow-demo`)

**Step 2: Upload Files**
Upload these files to your Space:
- `app.py`
- `agent.py`
- `storage.py`
- `monitor.py`
- `metrics.py`
- `mcp_tools.py`
- `requirements.txt`
- `README.md`
- `.env.example` (optional, for documentation)

**Step 3: Configure Environment Variables**

In Space Settings → Variables, add:

**Option A: With Demo AI (Recommended for Judges)**
```bash
LAUNCH_MODE=demo
AI_PROVIDER=anthropic
DEMO_ANTHROPIC_API_KEY=sk-ant-your-hackathon-shared-key
MONITOR_INTERVAL=30
ENABLE_MCP=true
```

**Option B: Mock AI Only (No API Keys Needed)**
```bash
LAUNCH_MODE=demo
AI_PROVIDER=mock
MONITOR_INTERVAL=30
ENABLE_MCP=true
```

**Step 4: Deploy**
- Click "Save" - Space will automatically rebuild and deploy
- Your app will be live at: `https://huggingface.co/spaces/yourusername/focusflow-demo`
- MCP server endpoint: `https://yourusername-focusflow-demo.hf.space/gradio_api/mcp/`

**Step 5: Test Deployment**
1. Open the Space URL
2. Test onboarding → Generate tasks
3. Test task manager → CRUD operations
4. Test monitor → Focus checks
5. Test dashboard → View metrics
6. Test MCP (optional) → Connect from Claude Desktop

### Deployment Option 2: Replit

**Step 1: Import Repository**
1. Go to https://replit.com
2. Click "Create Repl" → "Import from GitHub"
3. Paste your FocusFlow repository URL

**Step 2: Configure Secrets**
In Replit Secrets (Tools → Secrets):
```bash
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
LAUNCH_MODE=demo
```

**Step 3: Run**
```bash
python app.py
```

**Step 4: Share**
- Click "Share" button
- Copy the public URL
- MCP endpoint: `https://yourrepl.repl.co/gradio_api/mcp/`

### Deployment Option 3: Local Development

**Step 1: Clone Repository**
```bash
git clone https://github.com/yourusername/focusflow.git
cd focusflow
```

**Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Configure Environment**
```bash
# Copy example
cp .env.example .env

# Edit .env with your settings
nano .env  # or code .env, vim .env, etc.
```

**Step 4: Run**
```bash
# For local file monitoring
export LAUNCH_MODE=local
python app.py

# For demo mode (text area)
export LAUNCH_MODE=demo
python app.py
```

**Step 5: Access**
- Web UI: http://localhost:5000
- MCP endpoint: http://localhost:5000/gradio_api/mcp/

### Deployment Option 4: Docker (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV LAUNCH_MODE=demo
ENV AI_PROVIDER=mock
ENV ENABLE_MCP=true

EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t focusflow .
docker run -p 5000:5000 -e ANTHROPIC_API_KEY=your_key focusflow
```

### Post-Deployment Checklist

After deploying to any platform:

- [ ] App loads without errors
- [ ] Home tab shows correct AI provider status
- [ ] Onboarding generates tasks
- [ ] Task Manager CRUD operations work
- [ ] Monitor tab performs focus checks
- [ ] Dashboard displays metrics (after checks)
- [ ] Pomodoro timer functions
- [ ] MCP endpoint accessible (optional)
- [ ] No sensitive data exposed in logs
- [ ] Database file (`focusflow.db`) created successfully

### Environment Variables Reference (Deployment)

**Required:**
- `LAUNCH_MODE` - Always set to `demo` for web deployments

**Optional:**
- `AI_PROVIDER` - `anthropic`, `openai`, `vllm`, or `mock` (default: `anthropic`)
- `DEMO_ANTHROPIC_API_KEY` - For hackathon/shared deployments
- `DEMO_OPENAI_API_KEY` - Alternative demo provider
- `ANTHROPIC_API_KEY` - User's personal key
- `OPENAI_API_KEY` - User's personal key
- `MONITOR_INTERVAL` - Seconds between checks (default: 30)
- `ENABLE_MCP` - Enable MCP server (default: true)

### Deployment Troubleshooting

| Issue | Platform | Solution |
|-------|----------|----------|
| Import errors | HF Spaces | Check `requirements.txt` includes all dependencies |
| "Port already in use" | Local | Change port in `app.py` or kill process using port 5000 |
| MCP not accessible | All | Ensure `ENABLE_MCP=true` and check firewall settings |
| Database errors | HF Spaces | Ensure space has write permissions (SQLite needs filesystem) |
| Mock AI always active | All | Check environment variables are set correctly |
| Slow performance | HF Spaces | Free tier has limited resources - consider upgrading |

## 🛠️ Tech Stack

- **Frontend**: Gradio 5.0+ (Python UI framework)
- **Backend**: Python 3.11+
- **Database**: SQLite (zero-config persistence)
- **AI Providers**: OpenAI GPT-4, Anthropic Claude, Google Gemini, vLLM, or Mock
- **Voice**: ElevenLabs text-to-speech (optional)
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

- Built for the [Gradio MCP Hackathon](https://gradio.app) - competing for **Track 1: Building MCP**
- Voice integration powered by [ElevenLabs](https://elevenlabs.io) - competing for **$2,000 Best Use of ElevenLabs** sponsor award
- Inspired by Duolingo's encouraging UX
- Uses [Model Context Protocol](https://modelcontextprotocol.io) for LLM integration

---

**Made with ❤️ for developers with ADHD who just need a little nudge to stay focused.**

*Hoot hoot!* 🦉
