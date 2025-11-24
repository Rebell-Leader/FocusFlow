# FocusFlow AI Accountability Agent

## Overview
FocusFlow is an AI-powered "Accountability Buddy" that monitors your coding workspace and provides Duolingo-style nudges to keep you focused on your tasks.

## Tech Stack
- **Frontend/UI:** Gradio 6.0+
- **Backend:** Python 3.11
- **AI/LLM:** OpenAI (GPT-4o) / Anthropic (Claude 3.5 Sonnet) / vLLM (ibm-granite/granite-4.0-h-1b)
- **File Monitoring:** Watchdog library
- **Storage:** SQLite
- **Configuration:** Environment variables via python-dotenv

## Project Structure
```
.
├── app.py              # Main Gradio application
├── storage.py          # Task manager with SQLite CRUD
├── monitor.py          # File monitoring with watchdog
├── agent.py            # AI Focus Agent logic
├── requirements.txt    # Python dependencies
├── .env.example        # Environment configuration template
└── replit.md          # Project documentation
```

## Features
- **AI-powered project onboarding**: Breaks projects into 5-8 actionable micro-tasks
- **Task Manager**: Full CRUD operations with task completion tracking
- **Progress tracking**: Visual progress slider showing completion percentage
- **Real-time file monitoring**: Content-aware diff detection with privacy filters
- **Focus Agent**: Duolingo-style personality system (On Track, Distracted, Idle)
- **Browser notifications**: Desktop alerts when distracted status detected
- **Demo mode**: Text area monitoring for HuggingFace Spaces deployment
- **Local mode**: Real-time directory monitoring for actual workspaces
- **Multi-provider AI support**: OpenAI, Anthropic, or local vLLM inference

## Configuration
All settings are managed via environment variables (see `.env.example`):
- `LAUNCH_MODE`: "demo" (text area) or "local" (file system)
- `AI_PROVIDER`: "openai", "anthropic", or "vllm"
- `MONITOR_INTERVAL`: Check frequency in seconds (default: 30)
- API keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or vLLM endpoint settings

## Recent Changes
- 2025-11-24: **Row-Click Task Editing** - Click any table row to select and edit tasks:
  - Dual-panel design: "Add New Task" (left) vs "Edit Selected Task" (right)
  - Proper field labels: Title, Description, Duration (minutes), Status
  - Compact action buttons: Start, Done, Delete (no Task ID input needed)
  - Safe duration parsing: handles "30 min", "30 minutes", or "30" formats
  - Handler signature fixes: all action buttons return 8 values matching Gradio bindings
  - Selection feedback: "**Selected:** Task #X - Title" displayed
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
