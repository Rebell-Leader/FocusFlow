"""
FocusFlow: AI Accountability Agent with Gradio 5 Interface.
Configurable via environment variables for HuggingFace Spaces or local use.
"""
import gradio as gr
import os
import time
import threading
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv
from storage import TaskManager
from monitor import FileMonitor
from agent import FocusAgent

# Load environment variables
load_dotenv()

# Configuration from environment
LAUNCH_MODE = os.getenv("LAUNCH_MODE", "demo").lower()  # 'demo' or 'local'
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()  # 'openai', 'anthropic', or 'vllm'
MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", "30"))  # seconds

# Global state
task_manager = TaskManager()
file_monitor = FileMonitor()
focus_agent: Optional[FocusAgent] = None
monitoring_active = False
timer_active = False  # Track timer state globally
activity_log: List[str] = []
demo_text_content = ""  # For demo mode text monitoring


def initialize_agent() -> str:
    """Initialize the AI agent with fallback to vLLM if API keys are missing."""
    global focus_agent, AI_PROVIDER
    
    try:
        provider_to_use = AI_PROVIDER
        fallback_used = False
        
        if AI_PROVIDER == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                provider_to_use = "vllm"
                fallback_used = True
            else:
                focus_agent = FocusAgent(provider="anthropic", api_key=api_key)
        elif AI_PROVIDER == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                provider_to_use = "vllm"
                fallback_used = True
            else:
                focus_agent = FocusAgent(provider="openai", api_key=api_key)
        
        if provider_to_use == "vllm":
            focus_agent = FocusAgent(
                provider="vllm",
                api_key=os.getenv("VLLM_API_KEY", "EMPTY"),
                base_url=os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"),
                model=os.getenv("VLLM_MODEL", "ibm-granite/granite-4.0-h-1b")
            )
        
        if fallback_used:
            return f"⚠️ {AI_PROVIDER.upper()} API key not found. Using vLLM as fallback provider."
        else:
            return f"✅ {provider_to_use.upper()} agent initialized successfully!"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def process_onboarding(project_description: str) -> tuple:
    """Process onboarding and generate tasks."""
    if not focus_agent:
        return "❌ Please initialize agent first (check your environment variables)", get_task_dataframe(), 0
    
    if not project_description.strip():
        return "❌ Please describe your project", get_task_dataframe(), 0
    
    # Generate tasks
    tasks = focus_agent.get_onboarding_tasks(project_description)
    
    if not tasks:
        return "❌ Failed to generate tasks. Check your AI provider configuration.", get_task_dataframe(), 0
    
    # Add tasks to database
    task_manager.clear_all_tasks()
    for task in tasks:
        task_manager.add_task(
            title=task.get("title", "Untitled"),
            description=task.get("description", ""),
            estimated_duration=task.get("estimated_duration", "30 min")
        )
    
    return f"✅ Generated {len(tasks)} tasks! Go to Task Manager to start.", get_task_dataframe(), calculate_progress()


def get_task_dataframe():
    """Get tasks as a list for display."""
    tasks = task_manager.get_all_tasks()
    if not tasks:
        return []
    
    display_tasks = []
    for task in tasks:
        status_emoji = "✅" if task['status'] == "Done" else "🔄" if task['status'] == "In Progress" else "⏳"
        display_tasks.append([
            task['id'],
            task['title'],
            task['description'],
            f"{status_emoji} {task['status']}",
            task['estimated_duration']
        ])
    return display_tasks


def calculate_progress() -> float:
    """Calculate overall task completion percentage."""
    tasks = task_manager.get_all_tasks()
    if not tasks:
        return 0.0
    
    completed = sum(1 for task in tasks if task['status'] == "Done")
    return (completed / len(tasks)) * 100


def add_new_task(title: str, description: str, duration: str) -> tuple:
    """Add a new task."""
    if not title.strip():
        return "❌ Task title is required", get_task_dataframe(), calculate_progress()
    
    task_manager.add_task(title, description, duration)
    return "✅ Task added successfully!", get_task_dataframe(), calculate_progress()


def delete_task(task_id: str) -> tuple:
    """Delete a task by ID."""
    try:
        task_manager.delete_task(int(task_id))
        return "✅ Task deleted", get_task_dataframe(), calculate_progress()
    except Exception as e:
        return f"❌ Error: {str(e)}", get_task_dataframe(), calculate_progress()


def set_task_active(task_id: str) -> tuple:
    """Set a task as active (In Progress)."""
    try:
        task_manager.set_active_task(int(task_id))
        return "✅ Task set as active! Start working and I'll monitor your progress.", get_task_dataframe(), calculate_progress()
    except Exception as e:
        return f"❌ Error: {str(e)}", get_task_dataframe(), calculate_progress()


def mark_task_done(task_id: str) -> tuple:
    """Mark a task as completed (Done)."""
    try:
        task_manager.update_task(int(task_id), status="Done")
        return "✅ Task marked as completed! 🎉", get_task_dataframe(), calculate_progress()
    except Exception as e:
        return f"❌ Error: {str(e)}", get_task_dataframe(), calculate_progress()


def start_monitoring(watch_path: str) -> tuple:
    """Start file monitoring (local mode only)."""
    global monitoring_active, timer_active
    
    if LAUNCH_MODE == "demo":
        return "❌ File monitoring disabled in demo mode. Use the text area instead.", gr.update(active=False)
    
    if not watch_path or not os.path.exists(watch_path):
        monitoring_active = False
        timer_active = False
        return f"❌ Invalid path: {watch_path}", gr.update(active=False)
    
    try:
        file_monitor.start(watch_path)
        monitoring_active = True
        timer_active = True  # Sync timer state
        return f"✅ Monitoring started on: {watch_path}", gr.update(active=True)
    except Exception as e:
        monitoring_active = False
        timer_active = False
        return f"❌ Error: {str(e)}", gr.update(active=False)


def stop_monitoring() -> tuple:
    """Stop file monitoring."""
    global monitoring_active, timer_active
    file_monitor.stop()
    monitoring_active = False
    timer_active = False  # Sync timer state
    return "⏹️ Monitoring stopped", gr.update(active=False)


def update_demo_text(text: str) -> str:
    """Update demo text content (demo mode only)."""
    global demo_text_content
    demo_text_content = text
    return f"✅ Text updated ({len(text)} characters)"


def get_activity_summary() -> str:
    """Get recent activity summary."""
    if LAUNCH_MODE == "demo":
        return f"📝 Demo text content: {len(demo_text_content)} characters"
    
    if not monitoring_active:
        return "⏸️ Monitoring is not active"
    
    recent = file_monitor.get_recent_activity(5)
    if not recent:
        return "💤 No recent file activity"
    
    summary = []
    for event in recent:
        summary.append(f"• {event['type'].upper()}: {event['filename']}")
    
    return "\n".join(summary)


def run_focus_check() -> tuple:
    """Run the focus check analysis."""
    if not focus_agent:
        return "⚠️ Agent not initialized. Check environment variables.", None
    
    active_task = task_manager.get_active_task()
    
    # Get recent activity based on mode
    if LAUNCH_MODE == "demo":
        # In demo mode, create synthetic activity from text content
        recent_activity = [{
            'type': 'text_edit',
            'filename': 'demo_workspace',
            'content': demo_text_content[-500:] if demo_text_content else "",
            'timestamp': time.time()
        }] if demo_text_content else []
    else:
        recent_activity = file_monitor.get_recent_activity(10)
    
    result = focus_agent.analyze(active_task, recent_activity)
    
    verdict = result.get("verdict", "Unknown")
    message = result.get("message", "No message")
    
    # Determine emoji
    emoji = "✅" if verdict == "On Track" else "⚠️" if verdict == "Distracted" else "💤"
    
    log_entry = f"{emoji} [{verdict}] {message}"
    activity_log.append(log_entry)
    
    # Keep only last 20 entries
    if len(activity_log) > 20:
        activity_log.pop(0)
    
    # Trigger browser alert for distracted status
    alert_js = None
    if verdict == "Distracted":
        import json
        safe_message = json.dumps(message)
        alert_js = f"""
        () => {{
            if (Notification.permission === "granted") {{
                new Notification("FocusFlow Alert 🦉", {{
                    body: {safe_message},
                    icon: "https://em-content.zobj.net/thumbs/160/apple/354/owl_1f989.png"
                }});
            }}
            return null;
        }}
        """
    
    return "\n".join(activity_log), alert_js


# New UI for FocusFlow - Complete Redesign
# This will be integrated into app.py

# Build the Gradio interface
# Note: Gradio 6.0 - Users can access dark mode via URL: ?__theme=dark
with gr.Blocks(title="FocusFlow AI") as app:
    
    # Hidden component for browser alerts
    alert_trigger = gr.HTML(visible=False)
    
    # Auto-refresh timer
    timer = gr.Timer(value=MONITOR_INTERVAL, active=False)
    
    with gr.Tabs() as tabs:
        # Tab 1: Home/Landing Page
        with gr.Tab("🏠 Home"):
            gr.Markdown("""
            # 🦉 FocusFlow - Your AI Accountability Buddy
            
            Keep focused on your coding tasks with Duolingo-style nudges!
            """)
            
            # Status indicator
            init_status = gr.Textbox(label="Status", value="Initializing...", interactive=False, scale=1)
            
            gr.Markdown("""
            ## ✨ Features
            
            - **🎯 AI-Powered Project Planning**: Break down projects into actionable micro-tasks
            - **📊 Progress Tracking**: Visual progress monitoring with completion percentages
            - **👁️ Real-Time Monitoring**: Track your coding activity and stay focused
            - **🦉 Duolingo-Style Nudges**: Encouraging, sassy, and gentle reminders
            - **🔔 Browser Notifications**: Get alerted when you're distracted
            - **🚀 Multi-Provider AI**: OpenAI, Anthropic, or local vLLM support
            
            ## ⚙️ Current Configuration
            """)
            
            with gr.Row():
                gr.Markdown(f"**Mode:** `{LAUNCH_MODE.upper()}`")
                gr.Markdown(f"**AI Provider:** `{AI_PROVIDER.upper()}`")
                gr.Markdown(f"**Check Interval:** `{MONITOR_INTERVAL}s`")
            
            if LAUNCH_MODE == "demo":
                gr.Markdown("""
                > ℹ️ **Demo Mode**: Use the text area in Monitor tab to simulate your workspace.
                """)
            else:
                gr.Markdown("""
                > ℹ️ **Local Mode**: Monitor your actual project directory.
                """)
            
            gr.Markdown("""
            ---
            **Get Started:** Navigate to Onboarding → describe your project → manage tasks → start monitoring!
            """)
        
        # Tab 2: Onboarding
        with gr.Tab("🚀 Onboarding"):
            gr.Markdown("""
            ## AI-Powered Project Planning
            
            Describe your project and I'll break it down into actionable micro-tasks!
            """)
            
            project_input = gr.Textbox(
                label="What are you building?",
                placeholder="e.g., 'A Python web scraper that extracts product data from e-commerce sites'",
                lines=5
            )
            generate_btn = gr.Button("✨ Generate Tasks", variant="primary", size="lg")
            onboard_status = gr.Textbox(label="Status", interactive=False)
        
        # Tab 3: Task Manager
        with gr.Tab("📋 Tasks"):
            gr.Markdown("## Your Tasks")
            
            progress_bar = gr.Slider(
                label="Overall Progress",
                value=0,
                minimum=0,
                maximum=100,
                interactive=False
            )
            
            # Editable task table
            task_table = gr.Dataframe(
                headers=["ID", "Title", "Description", "Status", "Duration"],
                value=get_task_dataframe(),
                interactive=True,
                wrap=True
            )
            
            with gr.Row():
                save_table_btn = gr.Button("💾 Save Table Edits", variant="primary", size="sm")
                refresh_btn = gr.Button("🔄 Refresh", size="sm")
                add_blank_btn = gr.Button("➕ Add New Task", variant="secondary", size="sm")
            
            # Quick actions row
            gr.Markdown("### Quick Actions")
            with gr.Row():
                task_id_input = gr.Number(label="Task ID", value=1, minimum=1, precision=0)
                with gr.Column():
                    set_active_btn = gr.Button("▶️ Set Active", variant="secondary", size="sm")
                    mark_done_btn = gr.Button("✅ Mark Done", variant="secondary", size="sm")
                    delete_btn = gr.Button("🗑️ Delete", variant="stop", size="sm")
            
            action_status = gr.Textbox(label="Status", interactive=False)
        
        # Tab 4: Monitor
        with gr.Tab("👁️ Monitor"):
            gr.Markdown("## Focus Monitoring")
            
            # Initialize all variables to avoid unbound issues
            demo_textarea = None
            demo_update_btn = None
            demo_status = None
            watch_path_input = None
            start_monitor_btn = None
            stop_monitor_btn = None
            monitor_status = None
            
            # Mode-specific UI
            if LAUNCH_MODE == "demo":
                gr.Markdown("**Demo Workspace** - Edit the text below to simulate coding:")
                demo_textarea = gr.Textbox(
                    label="Your Code",
                    placeholder="Type or paste your code here...",
                    lines=8,
                    value="# Welcome to FocusFlow!\n# Start coding..."
                )
                demo_update_btn = gr.Button("💾 Save Changes", variant="secondary")
                demo_status = gr.Textbox(label="Status", interactive=False)
            else:
                gr.Markdown("**Directory Monitoring**")
                watch_path_input = gr.Textbox(
                    label="Path to Monitor",
                    value=os.getcwd(),
                    placeholder="/path/to/your/project"
                )
                with gr.Row():
                    start_monitor_btn = gr.Button("▶️ Start", variant="primary", size="sm")
                    stop_monitor_btn = gr.Button("⏹️ Stop", variant="stop", size="sm")
                monitor_status = gr.Textbox(label="Status", interactive=False)
            
            # Focus log (common for both modes)
            gr.Markdown("### 🦉 Focus Agent Log")
            focus_log = gr.Textbox(
                label="Activity Log",
                lines=12,
                interactive=False,
                placeholder="Focus checks will appear here..."
            )
            
            with gr.Row():
                manual_check_btn = gr.Button("🔍 Run Focus Check Now", variant="secondary")
                if LAUNCH_MODE == "demo":
                    timer_toggle_btn = gr.Button("⏸️ Pause Auto-Check", variant="secondary")
                else:
                    timer_toggle_btn = gr.Button("▶️ Start Auto-Check", variant="secondary")
    
    # Event handlers
    app.load(fn=initialize_agent, outputs=init_status)
    
    # Onboarding handlers
    generate_btn.click(
        fn=process_onboarding,
        inputs=project_input,
        outputs=[onboard_status, task_table, progress_bar]
    )
    
    # Task manager handlers
    refresh_btn.click(
        fn=lambda: (get_task_dataframe(), calculate_progress()),
        outputs=[task_table, progress_bar]
    )
    
    def add_blank_task():
        """Add a blank task row for inline editing."""
        task_manager.add_task(
            title="New Task",
            description="Edit this description",
            estimated_duration="30 min"
        )
        return get_task_dataframe(), calculate_progress()
    
    add_blank_btn.click(
        fn=add_blank_task,
        outputs=[task_table, progress_bar]
    )
    
    def save_table_edits(table_data):
        """Save inline edits from the task table."""
        try:
            if not table_data:
                return "❌ No data to save", get_task_dataframe(), calculate_progress()
            
            # Valid status values
            VALID_STATUSES = {"Done", "In Progress", "Not Started"}
            
            updated_count = 0
            for row in table_data:
                if len(row) >= 5:
                    task_id = int(row[0])
                    title = str(row[1])
                    description = str(row[2])
                    status_raw = str(row[3]).strip()
                    duration = str(row[4])
                    
                    # Normalize status: remove emoji prefix and trim
                    # Split on first space and take the rest
                    parts = status_raw.split(' ', 1)
                    status_cleaned = (parts[1] if len(parts) > 1 else parts[0]).strip()
                    
                    # Validate against allowed statuses
                    if status_cleaned not in VALID_STATUSES:
                        # Try case-insensitive match
                        status_match = None
                        for valid_status in VALID_STATUSES:
                            if status_cleaned.lower() == valid_status.lower():
                                status_match = valid_status
                                break
                        
                        if not status_match:
                            continue  # Skip invalid status rows
                        status = status_match
                    else:
                        status = status_cleaned
                    
                    # Update task
                    task_manager.update_task(
                        task_id,
                        title=title,
                        description=description,
                        status=status,
                        estimated_duration=duration
                    )
                    updated_count += 1
            
            return f"✅ Saved {updated_count} task(s)!", get_task_dataframe(), calculate_progress()
        except Exception as e:
            return f"❌ Error saving: {str(e)}", get_task_dataframe(), calculate_progress()
    
    save_table_btn.click(
        fn=save_table_edits,
        inputs=task_table,
        outputs=[action_status, task_table, progress_bar]
    )
    
    def quick_set_active(task_id):
        try:
            task_manager.set_active_task(int(task_id))
            return "✅ Task set as active!", get_task_dataframe(), calculate_progress()
        except Exception as e:
            return f"❌ Error: {str(e)}", get_task_dataframe(), calculate_progress()
    
    def quick_mark_done(task_id):
        try:
            task_manager.update_task(int(task_id), status="Done")
            return "✅ Task completed! 🎉", get_task_dataframe(), calculate_progress()
        except Exception as e:
            return f"❌ Error: {str(e)}", get_task_dataframe(), calculate_progress()
    
    def quick_delete(task_id):
        try:
            task_manager.delete_task(int(task_id))
            return "✅ Task deleted", get_task_dataframe(), calculate_progress()
        except Exception as e:
            return f"❌ Error: {str(e)}", get_task_dataframe(), calculate_progress()
    
    set_active_btn.click(
        fn=quick_set_active,
        inputs=task_id_input,
        outputs=[action_status, task_table, progress_bar]
    )
    
    mark_done_btn.click(
        fn=quick_mark_done,
        inputs=task_id_input,
        outputs=[action_status, task_table, progress_bar]
    )
    
    delete_btn.click(
        fn=quick_delete,
        inputs=task_id_input,
        outputs=[action_status, task_table, progress_bar]
    )
    
    # Monitor handlers
    if LAUNCH_MODE == "demo":
        if demo_update_btn and demo_textarea and demo_status:
            demo_update_btn.click(
                fn=update_demo_text,
                inputs=demo_textarea,
                outputs=demo_status
            )
    else:
        # Local mode monitoring with button label sync
        def start_monitoring_wrapper(watch_path):
            status, timer_update = start_monitoring(watch_path)
            # Only show "Pause" if timer actually started
            button_label = "⏸️ Pause Auto-Check" if timer_active else "▶️ Start Auto-Check"
            return status, timer_update, gr.update(value=button_label)
        
        def stop_monitoring_wrapper():
            status, timer_update = stop_monitoring()
            # Show "Start" when stopped
            button_label = "▶️ Start Auto-Check"
            return status, timer_update, gr.update(value=button_label)
        
        if start_monitor_btn and watch_path_input and monitor_status:
            start_monitor_btn.click(
                fn=start_monitoring_wrapper,
                inputs=watch_path_input,
                outputs=[monitor_status, timer, timer_toggle_btn]
            )
        
        if stop_monitor_btn and monitor_status:
            stop_monitor_btn.click(
                fn=stop_monitoring_wrapper,
                outputs=[monitor_status, timer, timer_toggle_btn]
            )
    
    manual_check_btn.click(
        fn=run_focus_check,
        outputs=[focus_log, alert_trigger]
    )
    
    # Timer toggle handler
    def toggle_timer():
        """Toggle the auto-check timer on/off."""
        global timer_active
        timer_active = not timer_active
        
        if timer_active:
            return gr.update(active=True), gr.update(value="⏸️ Pause Auto-Check")
        else:
            return gr.update(active=False), gr.update(value="▶️ Resume Auto-Check")
    
    timer_toggle_btn.click(
        fn=toggle_timer,
        outputs=[timer, timer_toggle_btn]
    )
    
    # Set timer active in demo mode on load
    if LAUNCH_MODE == "demo":
        def activate_timer_demo():
            global timer_active
            timer_active = True
            return gr.update(active=True)
        
        app.load(fn=activate_timer_demo, outputs=timer)
    
    # Timer tick handler
    def update_on_tick():
        """Update focus log on timer tick."""
        focus_result, alert_js = run_focus_check()
        
        alert_html = ""
        if alert_js:
            alert_html = f'<script>{alert_js}</script>'
        
        return focus_result, alert_html
    
    timer.tick(
        fn=update_on_tick,
        outputs=[focus_log, alert_trigger]
    )


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=5000, share=False)
