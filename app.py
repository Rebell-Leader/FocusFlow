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
    """Get tasks as a list for display (simplified - no emojis)."""
    tasks = task_manager.get_all_tasks()
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


def calculate_progress() -> float:
    """Calculate overall task completion percentage."""
    tasks = task_manager.get_all_tasks()
    if not tasks:
        return 0.0
    
    completed = sum(1 for task in tasks if task['status'] == "Done")
    return (completed / len(tasks)) * 100


def add_new_task(title: str, description: str, duration: int, status: str) -> tuple:
    """Add a new task with all fields."""
    if not title.strip():
        return "", "", 30, "Todo", get_task_dataframe(), calculate_progress()
    
    # Format duration as "{duration} min"
    duration_str = f"{duration} min"
    task_manager.add_task(title, description, duration_str, status)
    
    # Clear the input fields and refresh table
    return "", "", 30, "Todo", get_task_dataframe(), calculate_progress()


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
    
    # Trigger browser alert and audio for distracted/idle status
    alert_js = None
    if verdict in ["Distracted", "Idle"]:
        import json
        safe_message = json.dumps(message)
        alert_js = f"""
        () => {{
            const audio = document.getElementById('nudge-alert');
            if (audio) {{
                audio.play().catch(e => console.log('Audio play failed:', e));
            }}
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
            onboard_status = gr.Markdown("")  # Use Markdown instead of Textbox for status messages
        
        # Tab 3: Task Manager
        with gr.Tab("📋 Tasks"):
            gr.Markdown("## 📋 Your Tasks")
            
            # Compact header: Progress bar + Action buttons in one row
            with gr.Row():
                progress_bar = gr.Slider(
                    label="Overall Progress",
                    value=0,
                    minimum=0,
                    maximum=100,
                    interactive=False,
                    scale=3
                )
                with gr.Column(scale=1, min_width=250):
                    gr.Markdown("**Quick Actions:**")
                    with gr.Row():
                        start_task_btn = gr.Button("▶️ Start", size="sm", variant="secondary", scale=1)
                        mark_done_btn = gr.Button("✅ Done", size="sm", variant="secondary", scale=1)
                        delete_task_btn = gr.Button("🗑️ Delete", size="sm", variant="stop", scale=1)
            
            # State to hold selected task ID and form mode
            selected_task_id = gr.State(value=None)
            form_mode = gr.State(value="hidden")  # "hidden", "add", or "edit"
            
            # Table view - click on row to select
            gr.Markdown("**Click on a task row to edit it, or add a new task:**")
            task_table = gr.Dataframe(
                headers=["ID", "Title", "Description", "Status", "Duration (min)"],
                value=[],
                interactive=False,
                wrap=True
            )
            
            selection_info = gr.Markdown("_Click **+ Add Task** to create a new task, or click a row above to edit._")
            
            # Button to show Add form
            add_task_trigger_btn = gr.Button("➕ Add Task", variant="primary", size="sm")
            
            # Single dynamic form (hidden by default) - using Column for better visibility control
            with gr.Column(visible=False) as task_form:
                form_header = gr.Markdown("### ✏️ Task Form")
                form_title = gr.Textbox(label="Title", placeholder="Task title")
                form_desc = gr.Textbox(label="Description", placeholder="Describe the task", lines=2)
                with gr.Row():
                    form_duration = gr.Number(label="Duration (minutes)", value=30, minimum=5, maximum=480, step=5, scale=2)
                    form_status = gr.Dropdown(
                        label="Status", 
                        choices=["Todo", "In Progress", "Done"],
                        value="Todo",
                        scale=1
                    )
                with gr.Row():
                    form_save_btn = gr.Button("💾 Save", variant="primary", size="sm", scale=1)
                    form_cancel_btn = gr.Button("❌ Cancel", variant="secondary", size="sm", scale=1)
        
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
            
            # Pomodoro Timer
            gr.Markdown("### 🍅 Pomodoro Timer")
            with gr.Row():
                pomodoro_display = gr.HTML(value="""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 10px;">
                    <div id="pomodoro-time" style="font-size: 48px; font-weight: bold; color: white; font-family: monospace;">25:00</div>
                    <div id="pomodoro-status" style="font-size: 16px; color: #f0f0f0; margin-top: 5px;">Work Time</div>
                </div>
                <audio id="pomodoro-alert" preload="auto">
                    <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTUI" type="audio/wav">
                </audio>
                <audio id="nudge-alert" preload="auto">
                    <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTUI" type="audio/wav">
                </audio>
                <script>
                let pomodoroState = {
                    minutes: 25,
                    seconds: 0,
                    isRunning: false,
                    isWorkTime: true,
                    interval: null
                };
                
                function formatTime(mins, secs) {
                    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
                }
                
                function updateDisplay() {
                    const display = document.getElementById('pomodoro-time');
                    const status = document.getElementById('pomodoro-status');
                    if (display) {
                        display.textContent = formatTime(pomodoroState.minutes, pomodoroState.seconds);
                        status.textContent = pomodoroState.isWorkTime ? 'Work Time' : 'Break Time';
                    }
                }
                
                function playAlert() {
                    const audio = document.getElementById('pomodoro-alert');
                    if (audio) {
                        audio.play().catch(e => console.log('Audio play failed:', e));
                    }
                    if (Notification.permission === "granted") {
                        new Notification("Pomodoro Timer", {
                            body: pomodoroState.isWorkTime ? "Work session complete! Take a break." : "Break is over! Ready to work?",
                            icon: "https://em-content.zobj.net/thumbs/160/apple/354/tomato_1f345.png"
                        });
                    }
                }
                
                function tick() {
                    if (pomodoroState.seconds === 0) {
                        if (pomodoroState.minutes === 0) {
                            playAlert();
                            pomodoroState.isWorkTime = !pomodoroState.isWorkTime;
                            pomodoroState.minutes = pomodoroState.isWorkTime ? 25 : 5;
                            pomodoroState.seconds = 0;
                        } else {
                            pomodoroState.minutes--;
                            pomodoroState.seconds = 59;
                        }
                    } else {
                        pomodoroState.seconds--;
                    }
                    updateDisplay();
                }
                
                function startPomodoro() {
                    if (!pomodoroState.isRunning) {
                        pomodoroState.isRunning = true;
                        pomodoroState.interval = setInterval(tick, 1000);
                    }
                }
                
                function stopPomodoro() {
                    if (pomodoroState.isRunning) {
                        pomodoroState.isRunning = false;
                        clearInterval(pomodoroState.interval);
                    }
                }
                
                function resetPomodoro() {
                    stopPomodoro();
                    pomodoroState.minutes = 25;
                    pomodoroState.seconds = 0;
                    pomodoroState.isWorkTime = true;
                    updateDisplay();
                }
                </script>
                """)
            
            with gr.Row():
                pomodoro_start_btn = gr.Button("▶️ Start", size="sm", scale=1)
                pomodoro_stop_btn = gr.Button("⏸️ Pause", size="sm", scale=1)
                pomodoro_reset_btn = gr.Button("🔄 Reset", size="sm", scale=1)
            
            # Focus log (common for both modes)
            gr.Markdown("### 🦉 Focus Agent Log")
            focus_log = gr.Textbox(
                label="Activity Log",
                lines=8,
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
    
    # Show form in "add" mode
    def show_add_form():
        """Show the form for adding a new task."""
        return (
            gr.update(visible=True),  # task_form
            "### ➕ Add New Task",  # form_header
            "",  # form_title
            "",  # form_desc
            30,  # form_duration
            "Todo",  # form_status
            "add",  # form_mode
            None,  # selected_task_id
            "_Fill in the form below to add a new task._"  # selection_info
        )
    
    add_task_trigger_btn.click(
        fn=show_add_form,
        outputs=[task_form, form_header, form_title, form_desc, form_duration, form_status, form_mode, selected_task_id, selection_info]
    )
    
    # Row click handler - show form in "edit" mode with task data
    def on_task_select(evt: gr.SelectData):
        """Handle row click to show edit form with selected task."""
        if evt.index is None or len(evt.index) == 0:
            return (
                gr.update(visible=False),
                "### ✏️ Task Form",
                "",
                "",
                30,
                "Todo",
                "hidden",
                None,
                "_No task selected._"
            )
        
        row_index = evt.index[0]
        tasks = task_manager.get_all_tasks()
        
        if row_index >= len(tasks):
            return (
                gr.update(visible=False),
                "### ✏️ Task Form",
                "",
                "",
                30,
                "Todo",
                "hidden",
                None,
                "_Invalid selection._"
            )
        
        task = tasks[row_index]
        task_id = task['id']
        
        # Parse duration - extract leading digits to handle any format
        duration_str = task.get('estimated_duration', '30')
        try:
            import re
            # Extract first number from string (handles "30 min", "30 minutes", "30m", "30", etc.)
            match = re.search(r'\d+', str(duration_str))
            duration_num = int(match.group()) if match else 30
        except (ValueError, AttributeError, TypeError):
            duration_num = 30  # Default fallback
        
        return (
            gr.update(visible=True),  # task_form
            f"### ✏️ Edit Task #{task_id}",  # form_header
            task['title'] or "",  # form_title
            task['description'] or "",  # form_desc
            duration_num,  # form_duration
            task['status'] or "Todo",  # form_status
            "edit",  # form_mode
            task_id,  # selected_task_id
            f"**Editing:** Task #{task_id} - {task['title']}"  # selection_info
        )
    
    task_table.select(
        fn=on_task_select,
        outputs=[task_form, form_header, form_title, form_desc, form_duration, form_status, form_mode, selected_task_id, selection_info]
    )
    
    # Unified save handler - adds or updates based on mode
    def save_task_handler(mode, task_id, title, desc, duration, status, current_header):
        """Save task - add new or update existing based on mode."""
        if not title.strip():
            return (
                get_task_dataframe(),
                calculate_progress(),
                "❌ Title is required.",
                gr.update(visible=True),  # Keep form visible
                current_header,  # Keep current header text
                title,
                desc,
                duration,
                status,
                mode,
                task_id
            )
        
        # Format duration as "n min" for storage
        duration_str = f"{int(duration)} min" if duration else "30 min"
        
        try:
            if mode == "add":
                # Add new task
                task_manager.add_task(
                    title=title,
                    description=desc,
                    estimated_duration=duration_str,
                    status=status
                )
                message = f"✅ Task '{title}' added successfully!"
            else:  # mode == "edit"
                # Update existing task
                if task_id is None:
                    return (
                        get_task_dataframe(),
                        calculate_progress(),
                        "❌ No task selected for editing.",
                        gr.update(visible=False),
                        "### ✏️ Task Form",
                        "",
                        "",
                        30,
                        "Todo",
                        "hidden",
                        None
                    )
                
                task_manager.update_task(
                    task_id=int(task_id),
                    title=title,
                    description=desc,
                    estimated_duration=duration_str,
                    status=status
                )
                message = f"✅ Task #{task_id} updated successfully!"
            
            # Hide form and refresh table
            return (
                get_task_dataframe(),
                calculate_progress(),
                message,
                gr.update(visible=False),  # Hide form
                "### ✏️ Task Form",
                "",
                "",
                30,
                "Todo",
                "hidden",
                None
            )
        except Exception as e:
            # On error, keep the form visible with current header
            error_header = f"### ➕ Add New Task" if mode == "add" else f"### ✏️ Edit Task #{task_id}"
            return (
                get_task_dataframe(),
                calculate_progress(),
                f"❌ Error: {str(e)}",
                gr.update(visible=True),  # Keep form visible on error
                error_header,  # Rebuild header string based on mode
                title,
                desc,
                duration,
                status,
                mode,
                task_id
            )
    
    form_save_btn.click(
        fn=save_task_handler,
        inputs=[form_mode, selected_task_id, form_title, form_desc, form_duration, form_status, form_header],
        outputs=[task_table, progress_bar, selection_info, task_form, form_header, form_title, form_desc, form_duration, form_status, form_mode, selected_task_id]
    )
    
    # Cancel handler - hide form
    def cancel_form():
        """Hide the form and clear selection."""
        return (
            gr.update(visible=False),  # task_form
            "### ✏️ Task Form",
            "",
            "",
            30,
            "Todo",
            "hidden",
            None,
            "_Click **+ Add Task** to create a new task, or click a row above to edit._"
        )
    
    form_cancel_btn.click(
        fn=cancel_form,
        outputs=[task_form, form_header, form_title, form_desc, form_duration, form_status, form_mode, selected_task_id, selection_info]
    )
    
    # Action button handlers for selected task (compact, no form manipulation)
    def start_selected_task(task_id):
        """Set selected task as active/in progress."""
        if task_id is None or task_id == "":
            return (
                get_task_dataframe(),
                calculate_progress(),
                "_No task selected. Click on a row first._"
            )
        
        try:
            success = task_manager.set_active_task(int(task_id))
            if success:
                return (
                    get_task_dataframe(),
                    calculate_progress(),
                    f"▶️ Task #{task_id} set to In Progress!"
                )
            else:
                return (
                    get_task_dataframe(),
                    calculate_progress(),
                    f"⚠️ Could not start task (another task may already be in progress)"
                )
        except Exception as e:
            return (
                get_task_dataframe(),
                calculate_progress(),
                f"❌ Error: {str(e)}"
            )
    
    def mark_selected_done(task_id):
        """Mark selected task as done."""
        if task_id is None or task_id == "":
            return (
                get_task_dataframe(),
                calculate_progress(),
                "_No task selected. Click on a row first._"
            )
        
        try:
            task_manager.update_task(int(task_id), status="Done")
            return (
                get_task_dataframe(),
                calculate_progress(),
                f"✅ Task #{task_id} marked as Done!"
            )
        except Exception as e:
            return (
                get_task_dataframe(),
                calculate_progress(),
                f"❌ Error: {str(e)}"
            )
    
    def delete_selected_task(task_id):
        """Delete the selected task and clear selection state."""
        if task_id is None or task_id == "":
            return (
                get_task_dataframe(),
                calculate_progress(),
                "_No task selected. Click on a row first._",
                None
            )
        
        try:
            task_manager.delete_task(int(task_id))
            # Clear selection after successful delete
            return (
                get_task_dataframe(), 
                calculate_progress(), 
                f"🗑️ Task #{task_id} deleted.",
                None
            )
        except Exception as e:
            # On error, clear selection 
            return (
                get_task_dataframe(),
                calculate_progress(),
                f"❌ Error deleting task: {str(e)}",
                None
            )
    
    start_task_btn.click(
        fn=start_selected_task,
        inputs=[selected_task_id],
        outputs=[task_table, progress_bar, selection_info]
    )
    
    mark_done_btn.click(
        fn=mark_selected_done,
        inputs=[selected_task_id],
        outputs=[task_table, progress_bar, selection_info]
    )
    
    delete_task_btn.click(
        fn=delete_selected_task,
        inputs=[selected_task_id],
        outputs=[task_table, progress_bar, selection_info, selected_task_id]
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
    
    # Pomodoro timer handlers - inject JavaScript execution
    def trigger_pomodoro_start():
        return """<script>if(typeof startPomodoro === 'function') startPomodoro();</script>"""
    
    def trigger_pomodoro_stop():
        return """<script>if(typeof stopPomodoro === 'function') stopPomodoro();</script>"""
    
    def trigger_pomodoro_reset():
        return """<script>if(typeof resetPomodoro === 'function') resetPomodoro();</script>"""
    
    pomodoro_start_btn.click(fn=trigger_pomodoro_start, outputs=alert_trigger)
    pomodoro_stop_btn.click(fn=trigger_pomodoro_stop, outputs=alert_trigger)
    pomodoro_reset_btn.click(fn=trigger_pomodoro_reset, outputs=alert_trigger)
    
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
