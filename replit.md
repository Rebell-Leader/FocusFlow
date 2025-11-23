# FocusFlow AI Accountability Agent

## Overview
FocusFlow is an AI-powered "Accountability Buddy" that monitors your coding workspace and provides Duolingo-style nudges to keep you focused on your tasks.

## Tech Stack
- **Frontend/UI:** Gradio 5.0+
- **Backend:** Python 3.11
- **AI/LLM:** OpenAI (GPT-4o) / Anthropic (Claude 3.5 Sonnet)
- **File Monitoring:** Watchdog library
- **Storage:** SQLite

## Project Structure
```
.
├── app.py              # Main Gradio application
├── storage.py          # Task manager with SQLite CRUD
├── monitor.py          # File monitoring with watchdog
├── agent.py            # AI Focus Agent logic
├── requirements.txt    # Python dependencies
└── replit.md          # Project documentation
```

## Features
- AI-powered project onboarding (breaks projects into micro-tasks)
- Task Manager with CRUD operations
- Real-time file monitoring with content-aware diff detection
- Focus Agent with personality system (On Track, Distracted, Idle)
- Demo mode for HuggingFace Spaces deployment
- Local mode for monitoring actual workspace directories

## Recent Changes
- 2025-11-23: Initial project setup with modular architecture
- 2025-11-23: Added OpenAI and Anthropic integrations via Replit blueprints

## User Preferences
- Dark theme for Gradio UI
- Clean, documented Python code
- Modular architecture with separate concerns
