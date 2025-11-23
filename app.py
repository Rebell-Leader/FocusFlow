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
activity_log: List[str] = []
demo_text_content = ""  # For demo mode text monitoring


def initialize_agent() -> str:
    """Initialize the AI agent from environment configuration."""
    global focus_agent
    try:
        if AI_PROVIDER == "vllm":
            focus_agent = FocusAgent(
                provider="vllm",
                api_key=os.getenv("VLLM_API_KEY", "EMPTY"),
                base_url=os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"),
                model=os.getenv("VLLM_MODEL", "ibm-granite/granite-4.0-h-1b")
            )
        elif AI_PROVIDER == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return "❌ ANTHROPIC_API_KEY not found in environment"
            focus_agent = FocusAgent(provider="anthropic", api_key=api_key)
        else:  # openai (default)
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "❌ OPENAI_API_KEY not found in environment"
            focus_agent = FocusAgent(provider="openai", api_key=api_key)
        
        return f"✅ {AI_PROVIDER.upper()} agent initialized successfully!"
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
    global monitoring_active
    
    if LAUNCH_MODE == "demo":
        return "❌ File monitoring disabled in demo mode. Use the text area instead.", gr.update(active=False)
    
    if not watch_path or not os.path.exists(watch_path):
        monitoring_active = False
        return f"❌ Invalid path: {watch_path}", gr.update(active=False)
    
    try:
        file_monitor.start(watch_path)
        monitoring_active = True
        return f"✅ Monitoring started on: {watch_path}", gr.update(active=True)
    except Exception as e:
        monitoring_active = False
        return f"❌ Error: {str(e)}", gr.update(active=False)


def stop_monitoring() -> tuple:
    """Stop file monitoring."""
    global monitoring_active
    file_monitor.stop()
    monitoring_active = False
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


# Build the Gradio interface
# Note: Gradio 6.0 has different API for themes. Users can access dark mode via URL: ?__theme=dark
with gr.Blocks(title="FocusFlow AI") as app:
    gr.Markdown(f"""
    # 🦉 FocusFlow - Your AI Accountability Buddy
    Keep focused on your coding tasks with Duolingo-style nudges!
    
    **Mode:** {LAUNCH_MODE.upper()} | **AI Provider:** {AI_PROVIDER.upper()} | **Check Interval:** {MONITOR_INTERVAL}s
    """)
    
    # Info banner about available modes
    if LAUNCH_MODE == "demo":
        gr.Markdown("""
        ℹ️ **Demo Mode Active**: Use the text area to simulate your workspace. File monitoring is disabled.
        """)
    else:
        gr.Markdown("""
        ℹ️ **Local Mode Active**: Monitor your actual project directory. Demo text area is disabled.
        """)
    
    # Initialize agent on startup
    init_status = gr.Textbox(label="Agent Status", value="Initializing...", interactive=False)
    
    with gr.Tabs():
        # Tab 1: Onboarding
        with gr.Tab("🚀 Onboarding"):
            gr.Markdown(f"""
            ### AI-Powered Project Planning
            Current provider: **{AI_PROVIDER.upper()}**
            
            Describe your project and I'll break it down into actionable micro-tasks!
            """)
            
            project_input = gr.Textbox(
                label="What are you building?",
                placeholder="e.g., 'A Python web scraper that extracts product data from e-commerce sites'",
                lines=4
            )
            generate_btn = gr.Button("Generate Tasks", variant="primary", size="lg")
            onboard_status = gr.Textbox(label="Status", interactive=False)
        
        # Tab 2: Task Manager
        with gr.Tab("📋 Task Manager"):
            gr.Markdown("### Your Tasks")
            
            progress_bar = gr.Slider(label="Overall Progress (%)", value=0, minimum=0, maximum=100, interactive=False)
            
            refresh_btn = gr.Button("🔄 Refresh Tasks")
            
            task_table = gr.Dataframe(
                headers=["ID", "Title", "Description", "Status", "Duration"],
                value=get_task_dataframe(),
                interactive=False,
                wrap=True
            )
            
            gr.Markdown("### Task Actions")
            with gr.Row():
                task_id_input = gr.Textbox(label="Task ID", placeholder="1")
                action_dropdown = gr.Dropdown(
                    choices=["Set Active", "Mark Done", "Delete"],
                    value="Set Active",
                    label="Action"
                )
                action_btn = gr.Button("Execute", variant="primary")
            
            action_status = gr.Textbox(label="Status", interactive=False)
            
            gr.Markdown("### Add New Task")
            with gr.Row():
                new_title = gr.Textbox(label="Title", placeholder="Task title")
                new_desc = gr.Textbox(label="Description", placeholder="Task description")
                new_duration = gr.Textbox(label="Duration", placeholder="30 min")
            add_task_btn = gr.Button("Add Task", variant="secondary")
            add_status = gr.Textbox(label="Status", interactive=False)
        
        # Tab 3: Monitor Dashboard
        with gr.Tab("👁️ Monitor Dashboard"):
            gr.Markdown("### Focus Monitoring")
            
            # Demo mode: Text area
            if LAUNCH_MODE == "demo":
                gr.Markdown("**Demo Workspace** - Edit the text below to simulate coding activity:")
                demo_textarea = gr.Textbox(
                    label="Your Code/Text",
                    placeholder="Type or paste your code here...",
                    lines=10,
                    value="# Welcome to FocusFlow Demo!\n# Start typing to simulate coding activity..."
                )
                demo_update_btn = gr.Button("Update Workspace", variant="secondary")
                demo_status = gr.Textbox(label="Status", interactive=False)
                
                # Disable file monitoring UI
                gr.Markdown("_File monitoring is disabled in demo mode_")
                watch_path_input = gr.Textbox(
                    label="Directory to Monitor",
                    value="(Disabled in demo mode)",
                    interactive=False
                )
                start_monitor_btn = gr.Button("▶️ Start Monitoring", variant="secondary", interactive=False)
                stop_monitor_btn = gr.Button("⏹️ Stop Monitoring", variant="stop", interactive=False)
            
            # Local mode: File monitoring
            else:
                # Disable demo text area
                gr.Markdown("_Demo text area is disabled in local mode_")
                demo_textarea = gr.Textbox(
                    label="Demo Workspace (Disabled)",
                    value="(Demo mode not active)",
                    interactive=False,
                    lines=3
                )
                
                gr.Markdown("**File Monitoring** - Monitor your actual project directory:")
                watch_path_input = gr.Textbox(
                    label="Directory to Monitor",
                    placeholder="/path/to/your/project",
                    value=os.getcwd()
                )
                
                with gr.Row():
                    start_monitor_btn = gr.Button("▶️ Start Monitoring", variant="primary")
                    stop_monitor_btn = gr.Button("⏹️ Stop Monitoring", variant="stop")
            
            monitor_status = gr.Textbox(label="Monitor Status", interactive=False)
            
            gr.Markdown("### Live Activity Feed")
            activity_display = gr.Textbox(
                label="Recent Activity",
                lines=6,
                interactive=False
            )
            
            gr.Markdown("### Focus Analysis")
            focus_log = gr.Textbox(
                label="AI Focus Agent Log",
                lines=10,
                interactive=False
            )
            
            # Hidden component for browser alerts
            alert_trigger = gr.HTML(visible=False)
            
            manual_check_btn = gr.Button("🔍 Run Focus Check Now", variant="primary")
            
            # Auto-refresh timer
            timer = gr.Timer(value=MONITOR_INTERVAL, active=False)
    
    # Event handlers
    app.load(fn=initialize_agent, outputs=init_status)
    
    generate_btn.click(
        fn=process_onboarding,
        inputs=project_input,
        outputs=[onboard_status, task_table, progress_bar]
    )
    
    refresh_btn.click(
        fn=lambda: (get_task_dataframe(), calculate_progress()),
        outputs=[task_table, progress_bar]
    )
    
    def execute_task_action(task_id: str, action: str):
        if action == "Set Active":
            return set_task_active(task_id)
        elif action == "Mark Done":
            return mark_task_done(task_id)
        elif action == "Delete":
            return delete_task(task_id)
        return "Unknown action", get_task_dataframe(), calculate_progress()
    
    action_btn.click(
        fn=execute_task_action,
        inputs=[task_id_input, action_dropdown],
        outputs=[action_status, task_table, progress_bar]
    )
    
    add_task_btn.click(
        fn=add_new_task,
        inputs=[new_title, new_desc, new_duration],
        outputs=[add_status, task_table, progress_bar]
    )
    
    # Demo mode event handlers
    if LAUNCH_MODE == "demo":
        demo_update_btn.click(
            fn=update_demo_text,
            inputs=demo_textarea,
            outputs=demo_status
        )
        # Auto-activate timer in demo mode
        app.load(fn=lambda: gr.update(active=True), outputs=timer)
    
    # Local mode event handlers
    else:
        start_monitor_btn.click(
            fn=start_monitoring,
            inputs=watch_path_input,
            outputs=[monitor_status, timer]
        )
        
        stop_monitor_btn.click(
            fn=stop_monitoring,
            outputs=[monitor_status, timer]
        )
    
    manual_check_btn.click(
        fn=run_focus_check,
        outputs=[focus_log, alert_trigger]
    )
    
    def update_all_on_tick():
        """Update both focus log and activity display on timer tick."""
        focus_result, alert_js = run_focus_check()
        activity_result = get_activity_summary()
        
        # Return alert HTML if needed
        alert_html = ""
        if alert_js:
            alert_html = f'<script>{alert_js}</script>'
        
        return focus_result, activity_result, alert_html
    
    timer.tick(
        fn=update_all_on_tick,
        outputs=[focus_log, activity_display, alert_trigger]
    )


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=5000, share=False)
