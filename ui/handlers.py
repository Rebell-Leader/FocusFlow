"""
UI Event Handlers for FocusFlow.
"""
import os
import gradio as gr
import pandas as pd
from agent import FocusAgent, MockFocusAgent

class UIHandlers:
    def __init__(self, task_manager, file_monitor, metrics_tracker, focus_monitor, linear_client=None):
        self.task_manager = task_manager
        self.file_monitor = file_monitor
        self.metrics_tracker = metrics_tracker
        self.focus_monitor = focus_monitor
        self.linear_client = linear_client

        # State
        self.monitoring_active = False
        self.timer_active = False
        self.check_interval = 30 # Default

    def get_voice_status_ui(self) -> str:
        """Get voice integration status for UI display."""
        from voice import get_voice_status
        return get_voice_status()

    def initialize_agent(self, ai_provider: str) -> tuple:
        """
        Initialize the AI agent.
        Returns: (status_message, actual_provider_display)
        """
        try:
            use_mock = False
            focus_agent = None

            if ai_provider == "anthropic":
                api_key = os.getenv("DEMO_ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    use_mock = True
                else:
                    try:
                        focus_agent = FocusAgent(provider="anthropic", api_key=api_key)
                        key_type = "demo" if os.getenv("DEMO_ANTHROPIC_API_KEY") else "user"
                        self.focus_monitor.set_agent(focus_agent)
                        return (f"✅ Anthropic Claude initialized successfully ({key_type} key)",
                               f"**AI Provider:** `ANTHROPIC (Claude)`")
                    except Exception as e:
                        print(f"⚠️ Anthropic API error: {e}")
                        use_mock = True

            elif ai_provider == "openai":
                api_key = os.getenv("DEMO_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    use_mock = True
                else:
                    try:
                        focus_agent = FocusAgent(provider="openai", api_key=api_key)
                        key_type = "demo" if os.getenv("DEMO_OPENAI_API_KEY") else "user"
                        self.focus_monitor.set_agent(focus_agent)
                        return (f"✅ OpenAI GPT-4 initialized successfully ({key_type} key)",
                               f"**AI Provider:** `OPENAI (GPT-4o)`")
                    except Exception as e:
                        print(f"⚠️ OpenAI API error: {e}")
                        use_mock = True

            elif ai_provider == "gemini":
                api_key = os.getenv("DEMO_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
                if not api_key:
                    use_mock = True
                else:
                    try:
                        focus_agent = FocusAgent(provider="gemini", api_key=api_key)
                        key_type = "demo" if os.getenv("DEMO_GEMINI_API_KEY") else "user"
                        self.focus_monitor.set_agent(focus_agent)
                        return (f"✅ Google Gemini initialized successfully ({key_type} key)",
                               f"**AI Provider:** `GEMINI (Flash 2.0)`")
                    except Exception as e:
                        print(f"⚠️ Gemini API error: {e}")
                        use_mock = True

            elif ai_provider == "vllm":
                try:
                    focus_agent = FocusAgent(
                        provider="vllm",
                        api_key=os.getenv("VLLM_API_KEY", "EMPTY"),
                        base_url=os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"),
                        model=os.getenv("VLLM_MODEL", "ibm-granite/granite-4.0-h-1b")
                    )
                    if not focus_agent.connection_healthy:
                        use_mock = True
                    else:
                        self.focus_monitor.set_agent(focus_agent)
                        return (f"✅ vLLM initialized successfully!",
                               f"**AI Provider:** `VLLM (Local)`")
                except Exception as e:
                    print(f"⚠️ vLLM error: {e}")
                    use_mock = True

            # Use mock agent if no API keys or connections available
            if use_mock:
                focus_agent = MockFocusAgent()
                self.focus_monitor.set_agent(focus_agent)
                return (f"ℹ️ Running in DEMO MODE with Mock AI (no API keys needed). Perfect for testing! 🎭",
                       f"**AI Provider:** `MOCK AI (Demo Mode)`")

            # Fallback
            focus_agent = MockFocusAgent()
            self.focus_monitor.set_agent(focus_agent)
            return (f"ℹ️ Using Mock AI for demo",
                   f"**AI Provider:** `MOCK AI (Fallback)`")

        except Exception as e:
            focus_agent = MockFocusAgent()
            self.focus_monitor.set_agent(focus_agent)
            return (f"ℹ️ Using Mock AI for demo (Error: {str(e)}) 🎭",
                   f"**AI Provider:** `MOCK AI (Error Fallback)`")

    def reconfigure_agent(self, provider: str, api_key: str, eleven_key: str) -> tuple:
        """
        Re-configure the agent with user-provided keys (Demo Mode).
        """
        # Update Environment Variables
        if api_key.strip():
            if provider == "openai":
                os.environ["OPENAI_API_KEY"] = api_key
            elif provider == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif provider == "gemini":
                os.environ["GEMINI_API_KEY"] = api_key

        if eleven_key.strip():
            os.environ["ELEVEN_API_KEY"] = eleven_key
            # Re-init voice
            from voice import voice_generator
            voice_generator.initialize()

        # Re-initialize Agent
        return self.initialize_agent(provider)

    def process_onboarding(self, project_description: str) -> tuple:
        """Process onboarding and generate tasks."""
        # Default UI updates for failure cases (no change to timer/monitoring)
        no_update = gr.update()

        if not self.focus_monitor.focus_agent:
            return "❌ Please initialize agent first", self.get_task_dataframe(), 0, no_update, no_update, no_update, no_update

        if not project_description.strip():
            return "❌ Please describe your project", self.get_task_dataframe(), 0, no_update, no_update, no_update, no_update

        # Generate tasks
        tasks = self.focus_monitor.focus_agent.get_onboarding_tasks(project_description)

        if not tasks:
            return "❌ Failed to generate tasks. Check your AI provider configuration.", self.get_task_dataframe(), 0, no_update, no_update, no_update, no_update

        # Reset State (Demo Mode Reset)
        # We clear everything to give the user a fresh start
        self.task_manager.clear_all_tasks()
        self.metrics_tracker.clear_all_data()
        self.stop_monitoring() # Stop backend monitoring

        # Add tasks to database
        for task in tasks:
            self.task_manager.add_task(
                title=task.get("title", "Untitled"),
                description=task.get("description", ""),
                estimated_duration=task.get("estimated_duration", "30 min")
            )

        # Return success with UI resets
        # Outputs: [onboard_status, task_table, progress_bar, monitor_timer, timer_toggle_btn, timer_active_state, demo_status]
        return (
            f"✅ Generated {len(tasks)} tasks! Go to Task Manager to start.",
            self.get_task_dataframe(),
            self.calculate_progress(),
            gr.update(active=False), # Stop timer
            gr.update(value="▶️ Start Auto-Check"), # Reset button label
            False, # Reset timer state
            "⏹️ Monitoring reset (New Project)" # Update status
        )

    def get_task_dataframe(self):
        """Get tasks as a list for display."""
        tasks = self.task_manager.get_all_tasks()
        if not tasks:
            return []

        display_tasks = []
        for task in tasks:
            display_tasks.append([
                task['id'],
                task['title'],
                task['description'],
                task['status'],
                task['estimated_duration']
            ])
        return display_tasks

    def calculate_progress(self) -> float:
        """Calculate overall task completion percentage."""
        tasks = self.task_manager.get_all_tasks()
        if not tasks:
            return 0.0

        completed = sum(1 for task in tasks if task['status'] == "Done")
        return (completed / len(tasks)) * 100

    def add_new_task(self, title: str, description: str, duration: int, status: str) -> tuple:
        """Add a new task."""
        if not title.strip():
            return "", "", 30, "Todo", self.get_task_dataframe(), self.calculate_progress()

        duration_str = f"{duration} min"
        self.task_manager.add_task(title, description, duration_str, status)
        return "", "", 30, "Todo", self.get_task_dataframe(), self.calculate_progress()

    def delete_task(self, task_id: str) -> tuple:
        """Delete a task by ID."""
        try:
            self.task_manager.delete_task(int(task_id))
            return "✅ Task deleted", self.get_task_dataframe(), self.calculate_progress()
        except Exception as e:
            return f"❌ Error: {str(e)}", self.get_task_dataframe(), self.calculate_progress()

    def set_task_active(self, task_id: str) -> tuple:
        """Set a task as active."""
        try:
            self.task_manager.set_active_task(int(task_id))
            return "✅ Task set as active! Start working and I'll monitor your progress.", self.get_task_dataframe(), self.calculate_progress()
        except Exception as e:
            return f"❌ Error: {str(e)}", self.get_task_dataframe(), self.calculate_progress()

    def mark_task_done(self, task_id: str) -> tuple:
        """Mark a task as completed."""
        try:
            self.task_manager.update_task(int(task_id), status="Done")
            return "✅ Task marked as completed! 🎉", self.get_task_dataframe(), self.calculate_progress()
        except Exception as e:
            return f"❌ Error: {str(e)}", self.get_task_dataframe(), self.calculate_progress()

    def start_monitoring(self, watch_path: str, launch_mode: str) -> tuple:
        """Start file monitoring."""
        if launch_mode == "demo":
            return "❌ File monitoring disabled in demo mode. Use the text area instead.", gr.update(active=False)

        if not watch_path or not os.path.exists(watch_path):
            self.monitoring_active = False
            self.timer_active = False
            return f"❌ Invalid path: {watch_path}", gr.update(active=False)

        try:
            self.file_monitor.start(watch_path)
            self.monitoring_active = True
            self.timer_active = True
            return f"✅ Monitoring started on: {watch_path}", gr.update(active=True)
        except Exception as e:
            self.monitoring_active = False
            self.timer_active = False
            return f"❌ Error: {str(e)}", gr.update(active=False)

    def stop_monitoring(self) -> tuple:
        """Stop file monitoring."""
        self.file_monitor.stop()
        self.monitoring_active = False
        self.timer_active = False
        return "⏹️ Monitoring stopped", gr.update(active=False)

    def set_check_interval(self, frequency_label: str) -> tuple:
        """Update check interval based on dropdown selection."""
        frequency_map = {
            "30 seconds": 30,
            "1 minute": 60,
            "5 minutes": 300,
            "10 minutes": 600,
        }

        self.check_interval = frequency_map.get(frequency_label, 30)
        # Return updated timer component
        return (
            gr.Timer(value=self.check_interval, active=self.timer_active),
            f"✅ Check interval set to {frequency_label}"
        )

    def refresh_dashboard(self) -> tuple:
        """Refresh dashboard with latest metrics."""
        today_stats = self.metrics_tracker.get_today_stats()
        current_streak = self.metrics_tracker.get_current_streak()

        state_data = pd.DataFrame([
            {"state": "On Track", "count": today_stats["on_track"]},
            {"state": "Distracted", "count": today_stats["distracted"]},
            {"state": "Idle", "count": today_stats["idle"]}
        ])

        chart_data = self.metrics_tracker.get_chart_data()
        weekly_data = pd.DataFrame({
            "date": chart_data["dates"],
            "score": chart_data["focus_scores"]
        })

        return (
            today_stats["focus_score"],
            current_streak,
            today_stats["total_checks"],
            state_data,
            weekly_data
        )

    # Linear Integration
    def get_linear_projects_ui(self):
        """Get Linear projects for dropdown."""
        if not self.linear_client:
             return gr.update(choices=[], value=None, visible=True), "⚠️ Linear client not initialized"

        projects = self.linear_client.get_user_projects()
        if not projects:
            return gr.update(choices=[], value=None, visible=True), "⚠️ No projects found (or API key missing)"

        choices = [(p['name'], p['id']) for p in projects]
        return gr.update(choices=choices, value=choices[0][1] if choices else None, visible=True), f"✅ Found {len(projects)} projects"

    def import_linear_tasks_ui(self, project_id):
        """Import tasks from selected Linear project."""
        if not self.linear_client:
             return "⚠️ Linear client not initialized", self.get_task_dataframe(), self.calculate_progress()

        if not project_id:
            return "❌ Select a project first", self.get_task_dataframe(), self.calculate_progress()

        tasks = self.linear_client.get_project_tasks(project_id)
        if not tasks:
            return "⚠️ No open tasks found in this project", self.get_task_dataframe(), self.calculate_progress()

        count = 0
        for t in tasks:
            estimate = t.get('estimate', 30) or 30
            duration_str = f"{estimate} min"
            self.task_manager.add_task(
                title=t['title'],
                description=t.get('description', ''),
                estimated_duration=duration_str,
                status="Todo"
            )
            count += 1

        return f"✅ Imported {count} tasks from Linear!", self.get_task_dataframe(), self.calculate_progress()
