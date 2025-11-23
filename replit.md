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
- 2025-11-23: Initial project setup with modular architecture
- 2025-11-23: Added OpenAI and Anthropic integrations via Replit blueprints
- 2025-11-23: Added vLLM support for local inference (ibm-granite/granite-4.0-h-1b)
- 2025-11-23: Implemented environment-based configuration system
- 2025-11-23: Added task completion tracking and progress bar
- 2025-11-23: Implemented browser notifications for distracted status
- 2025-11-23: Separated demo and local modes with conditional UI
- 2025-11-23: Fixed Gradio 6.0 API compatibility issues
- 2025-11-23: Fixed vLLM provider handling in onboarding and monitoring
- 2025-11-23: Improved JavaScript notification security with proper escaping

## User Preferences
- Dark theme for Gradio UI (access via URL parameter: ?__theme=dark)
- Clean, documented Python code
- Modular architecture with separate concerns
- Environment-based configuration (no UI settings)
