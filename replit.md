# FocusFlow AI Accountability Agent

## Overview
FocusFlow is an AI-powered "Accountability Buddy" that monitors your coding workspace and provides Duolingo-style nudges to keep you focused on your tasks.

## Tech Stack
- **Frontend/UI:** Gradio 6.0+
- **Backend:** Python 3.11
- **AI/LLM:** OpenAI (GPT-4o) / Anthropic (Claude 3.5 Sonnet) / Google Gemini (gemini-2.0-flash-exp) / vLLM (ibm-granite/granite-4.0-h-1b)
- **File Monitoring:** Watchdog library
- **Storage:** SQLite
- **Configuration:** Environment variables via python-dotenv

## Project Structure
```
.
├── app.py              # Main Gradio application (5 tabs)
├── agent.py            # AI Focus Agent (FocusAgent + MockFocusAgent)
├── storage.py          # Task manager with SQLite CRUD
├── monitor.py          # File monitoring with watchdog
├── metrics.py          # Productivity metrics tracking
├── mcp_tools.py        # MCP tools and resources
├── requirements.txt    # Python dependencies
├── .env.example        # Environment configuration template
├── README.md           # Comprehensive project documentation
└── replit.md           # Technical project notes
```

## Features
- **MCP Integration**: Full Model Context Protocol support for Claude Desktop and other LLM clients
- **AI-powered project onboarding**: Breaks projects into 5-8 actionable micro-tasks
- **Mock Agent mode**: Works without API keys for demo/testing purposes
- **Task Manager**: Full CRUD operations with task completion tracking
- **Productivity Dashboard**: Focus scores, streaks, weekly trends, and visualizations
- **Progress tracking**: Visual progress slider showing completion percentage
- **Real-time file monitoring**: Content-aware diff detection with privacy filters
- **Focus Agent**: Duolingo-style personality system (On Track, Distracted, Idle)
- **Browser notifications**: Desktop alerts when distracted status detected
- **Pomodoro Timer**: 25+5 work/break cycles with audio alerts
- **Demo mode**: Text area monitoring for HuggingFace Spaces deployment
- **Local mode**: Real-time directory monitoring for actual workspaces
- **Multi-provider AI support**: OpenAI, Anthropic, vLLM, or Mock

## Configuration
All settings are managed via environment variables (see `.env.example`):
- `LAUNCH_MODE`: "demo" (text area) or "local" (file system)
- `AI_PROVIDER`: "openai", "anthropic", "gemini", or "vllm"
- `MONITOR_INTERVAL`: Check frequency in seconds (default: 30)
- API keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, or vLLM endpoint settings

## Recent Changes
- 2025-11-26: **Google Gemini AI Provider Added** - 4th AI provider option:
  - Added Google Gemini (gemini-2.0-flash-exp) support to agent.py
  - Installed google-generativeai package
  - Updated .env.example with GEMINI_API_KEY and DEMO_GEMINI_API_KEY
  - Updated README.md with Gemini installation and configuration
  - Full feature parity with OpenAI, Anthropic, and vLLM providers
- 2025-11-26: **MCP Integration Complete** - Full Model Context Protocol support:
  - 8 MCP tools exposed: add_task, get_current_task, start_task, mark_task_done, get_all_tasks, delete_task, get_productivity_stats
  - 3 MCP resources: focusflow://tasks/all, focusflow://tasks/active, focusflow://stats
  - MCP server runs on http://localhost:5000/gradio_api/mcp/
  - Compatible with Claude Desktop, Cursor, Cline, and other MCP clients
  - Natural language task management through LLM integration
- 2025-11-26: **Mock Agent for Demo Mode** - Works without API keys:
  - MockFocusAgent class provides predefined responses
  - Cycles through "On Track", "Distracted", "Idle" verdicts
  - Keyword-based task generation for onboarding
  - Perfect for testing and HuggingFace Spaces deployment
- 2025-11-26: **Productivity Dashboard** - Complete metrics tracking:
  - MetricsTracker module with SQLite persistence
  - Focus score (0-100) based on on-track percentage
  - Streak tracking (consecutive On Track checks)
  - Weekly trend visualization (last 7 days)
  - State distribution charts (BarPlot)
  - Automatic metrics logging on each focus check
- 2025-11-26: **Dashboard Tab UI** - Visual analytics interface:
  - Today's stats: Focus Score, Current Streak, Total Checks
  - Focus States Distribution (bar chart)
  - Weekly Focus Score Trend (line chart)
  - Refresh button for real-time updates
  - Auto-refresh on page load
- 2025-11-24: **Form Collapse Fixed** - Forms now collapse after save/cancel:
  - JavaScript callbacks on Save/Cancel buttons hide form completely
  - `.then()` with `js="() => { ... display: 'none' }"` implementation
  - "+" Add Task button uses JavaScript to show form: `display: 'block'`
  - Form properly hides after both successful saves and error handling
- 2025-11-24: **Pomodoro Timer Fully Functional**:
  - All control buttons now connected: Start, Pause, Reset
  - JavaScript event handlers added: `startPomodoro()`, `stopPomodoro()`, `resetPomodoro()`
  - Countdown works: 25 min work → 5 min break cycles
  - Audio alerts on completion + browser notifications
  - Status display switches: "Work Time" ↔ "Break Time"
- 2025-11-24: **Clean Single-Form UI** - Collapsed duplicate add/edit forms into dynamic single form:
  - Single hidden form shown on-demand ("+ Add Task" button or click table row)
  - Dynamic header changes based on mode ("Add New Task" vs "Edit Task #X")
  - Form modes: hidden, add, edit (tracked via form_mode State)
  - Save button intelligently adds or updates based on current mode
  - Cancel button hides form and clears selection
- 2025-11-24: **Compact Action Buttons** - Merged with progress bar at top:
  - Progress bar + Quick Actions in single horizontal Row
  - Three compact buttons: Start, Done, Delete (work on selected task)
  - No form field manipulation from action buttons
- 2025-11-24: **Row-Click Task Selection** - Click any table row to edit:
  - Click table row → Form appears with task data populated
  - Proper field labels: Title, Description, Duration (minutes), Status
  - Safe duration parsing: handles multiple formats
  - Selection feedback: "**Editing:** Task #X - Title" displayed
- 2025-11-24: **Pomodoro Timer (25+5)** on Monitor page:
  - Visual countdown display with gradient background
  - Work/Break mode auto-switching
  - Start/Pause/Reset controls
  - Browser notifications and audio alerts on completion
- 2025-11-24: **Audio Alerts**:
  - Pomodoro timer completion sound + notification
  - AI nudge alert sound for Distracted/Idle status
  - HTML5 audio elements with base64 encoded sounds
- 2025-11-24: **vLLM Connection Management**:
  - Health check with timeout at initialization
  - Clear error messages when server unavailable
  - Graceful degradation in AI features
- 2025-11-24: **Strict Data Model Enforcement**:
  - Status enum: Todo, In Progress, Done (validated in storage layer)
  - Single "In Progress" task rule (enforced transactionally)
  - Duration stored as "{n} min" string, displayed as number input
- 2025-11-24: **UI Cleanup**:
  - Removed Status blocks from Onboarding and Tasks pages
  - Status feedback only on Monitor page
- 2025-11-23: Complete UI/UX redesign with landing page and cleaner navigation
- 2025-11-23: Implemented vLLM as automatic fallback when API keys missing

## User Preferences
- Dark theme for Gradio UI (access via URL parameter: ?__theme=dark)
- Clean, documented Python code
- Modular architecture with separate concerns
- Environment-based configuration (no UI settings)
