"""
FocusFlow: AI Accountability Agent with Gradio 5 Interface.
"""
import gradio as gr
import os
import time
import threading
from pathlib import Path
from typing import Optional, List, Dict
from storage import TaskManager
from monitor import FileMonitor
from agent import FocusAgent

# Global state
task_manager = TaskManager()
file_monitor = FileMonitor()
focus_agent: Optional[FocusAgent] = None
monitoring_active = False
activity_log: List[str] = []
demo_mode = False


def initialize_agent(provider: str, api_key: str) -> str:
    """Initialize the AI agent with API key."""
    global focus_agent
    try:
        focus_agent = FocusAgent(provider=provider, api_key=api_key)
        return f"✅ {provider.capitalize()} agent initialized successfully!"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def process_onboarding(project_description: str) -> tuple:
    """Process onboarding and generate tasks."""
    if not focus_agent:
        return "❌ Please configure API key first", get_task_dataframe()
    
    if not project_description.strip():
        return "❌ Please describe your project", get_task_dataframe()
    
    # Generate tasks
    tasks = focus_agent.get_onboarding_tasks(project_description)
    
    if not tasks:
        return "❌ Failed to generate tasks. Check your API key.", get_task_dataframe()
    
    # Add tasks to database
    task_manager.clear_all_tasks()
    for task in tasks:
        task_manager.add_task(
            title=task.get("title", "Untitled"),
            description=task.get("description", ""),
            estimated_duration=task.get("estimated_duration", "30 min")
        )
    
    return f"✅ Generated {len(tasks)} tasks! Go to Task Manager to start.", get_task_dataframe()


def get_task_dataframe():
    """Get tasks as a list for display."""
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


def add_new_task(title: str, description: str, duration: str) -> tuple:
    """Add a new task."""
    if not title.strip():
        return "❌ Task title is required", get_task_dataframe()
    
    task_manager.add_task(title, description, duration)
    return "✅ Task added successfully!", get_task_dataframe()


def delete_task(task_id: str) -> tuple:
    """Delete a task by ID."""
    try:
        task_manager.delete_task(int(task_id))
        return "✅ Task deleted", get_task_dataframe()
    except Exception as e:
        return f"❌ Error: {str(e)}", get_task_dataframe()


def set_task_active(task_id: str) -> tuple:
    """Set a task as active."""
    try:
        task_manager.set_active_task(int(task_id))
        return "✅ Task set as active! Start working and I'll monitor your progress.", get_task_dataframe()
    except Exception as e:
        return f"❌ Error: {str(e)}", get_task_dataframe()


def start_monitoring(watch_path: str, use_demo: bool) -> tuple:
    """Start file monitoring. Returns (status_message, should_activate_timer)."""
    global monitoring_active, demo_mode
    
    demo_mode = use_demo
    
    if demo_mode:
        # Create demo workspace
        demo_path = Path("demo_workspace")
        demo_path.mkdir(exist_ok=True)
        (demo_path / "main.py").write_text("# Demo file for FocusFlow\nprint('Hello World')")
        watch_path = str(demo_path)
    
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
    """Stop file monitoring. Returns (status_message, should_deactivate_timer)."""
    global monitoring_active
    file_monitor.stop()
    monitoring_active = False
    return "⏹️ Monitoring stopped", gr.update(active=False)


def get_activity_summary() -> str:
    """Get recent activity summary."""
    if not monitoring_active:
        return "⏸️ Monitoring is not active"
    
    recent = file_monitor.get_recent_activity(5)
    if not recent:
        return "💤 No recent file activity"
    
    summary = []
    for event in recent:
        summary.append(f"• {event['type'].upper()}: {event['filename']}")
    
    return "\n".join(summary)


def run_focus_check() -> str:
    """Run the focus check analysis."""
    if not focus_agent:
        return "⚠️ Agent not initialized. Configure API key in Settings."
    
    active_task = task_manager.get_active_task()
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
    
    return "\n".join(activity_log)


def simulate_demo_activity() -> str:
    """Simulate file activity in demo mode."""
    if not demo_mode:
        return "Demo mode is not active"
    
    demo_path = Path("demo_workspace")
    test_file = demo_path / "main.py"
    
    # Append some code to trigger an event
    with open(test_file, "a") as f:
        f.write(f"\n# Simulated edit at {time.time()}")
    
    time.sleep(0.5)
    return get_activity_summary()


# Build the Gradio interface
# Note: Gradio 6.0 has different API for themes. Users can access dark mode via URL: ?__theme=dark
with gr.Blocks(title="FocusFlow AI") as app:
    gr.Markdown("""
    # 🦉 FocusFlow - Your AI Accountability Buddy
    Keep focused on your coding tasks with Duolingo-style nudges!
    """)
    
    with gr.Tabs():
        # Tab 1: Setup & Onboarding
        with gr.Tab("🚀 Setup & Onboarding"):
            gr.Markdown("### Step 1: Configure AI Provider")
            with gr.Row():
                provider_choice = gr.Dropdown(
                    choices=["openai", "anthropic"],
                    value="openai",
                    label="AI Provider"
                )
                api_key_input = gr.Textbox(
                    label="API Key",
                    type="password",
                    placeholder="sk-..."
                )
                init_btn = gr.Button("Initialize Agent", variant="primary")
            
            init_status = gr.Textbox(label="Status", interactive=False)
            
            gr.Markdown("### Step 2: Describe Your Project")
            project_input = gr.Textbox(
                label="What are you building?",
                placeholder="e.g., 'A React todo app with authentication'",
                lines=3
            )
            generate_btn = gr.Button("Generate Tasks", variant="primary", size="lg")
            onboard_status = gr.Textbox(label="Status", interactive=False)
        
        # Tab 2: Task Manager
        with gr.Tab("📋 Task Manager"):
            gr.Markdown("### Your Tasks")
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
                    choices=["Set Active", "Delete"],
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
            gr.Markdown("### File Monitoring")
            
            with gr.Row():
                use_demo_check = gr.Checkbox(label="Demo Mode (for HuggingFace Spaces)", value=False)
                watch_path_input = gr.Textbox(
                    label="Directory to Monitor",
                    placeholder="/path/to/your/project (or leave empty for demo)",
                    value=""
                )
            
            with gr.Row():
                start_monitor_btn = gr.Button("▶️ Start Monitoring", variant="primary")
                stop_monitor_btn = gr.Button("⏹️ Stop Monitoring", variant="stop")
            
            monitor_status = gr.Textbox(label="Monitor Status", interactive=False)
            
            gr.Markdown("### Live Activity Feed")
            activity_display = gr.Textbox(
                label="Recent File Changes",
                lines=6,
                interactive=False
            )
            
            if_demo_btn = gr.Button("🎬 Simulate Activity (Demo Mode Only)", variant="secondary")
            
            gr.Markdown("### Focus Analysis")
            focus_log = gr.Textbox(
                label="AI Focus Agent Log",
                lines=10,
                interactive=False
            )
            
            manual_check_btn = gr.Button("🔍 Run Focus Check Now", variant="primary")
            
            # Auto-refresh timer
            timer = gr.Timer(value=30, active=False)
    
    # Event handlers
    init_btn.click(
        fn=initialize_agent,
        inputs=[provider_choice, api_key_input],
        outputs=init_status
    )
    
    generate_btn.click(
        fn=process_onboarding,
        inputs=project_input,
        outputs=[onboard_status, task_table]
    )
    
    refresh_btn.click(
        fn=lambda: get_task_dataframe(),
        outputs=task_table
    )
    
    def execute_task_action(task_id: str, action: str):
        if action == "Set Active":
            return set_task_active(task_id)
        elif action == "Delete":
            return delete_task(task_id)
        return "Unknown action", get_task_dataframe()
    
    action_btn.click(
        fn=execute_task_action,
        inputs=[task_id_input, action_dropdown],
        outputs=[action_status, task_table]
    )
    
    add_task_btn.click(
        fn=add_new_task,
        inputs=[new_title, new_desc, new_duration],
        outputs=[add_status, task_table]
    )
    
    start_monitor_btn.click(
        fn=start_monitoring,
        inputs=[watch_path_input, use_demo_check],
        outputs=[monitor_status, timer]
    )
    
    stop_monitor_btn.click(
        fn=stop_monitoring,
        outputs=[monitor_status, timer]
    )
    
    manual_check_btn.click(
        fn=run_focus_check,
        outputs=focus_log
    )
    
    if_demo_btn.click(
        fn=simulate_demo_activity,
        outputs=activity_display
    )
    
    def update_all_on_tick():
        """Update both focus log and activity display on timer tick."""
        return run_focus_check(), get_activity_summary()
    
    timer.tick(
        fn=update_all_on_tick,
        outputs=[focus_log, activity_display]
    )


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=5000, share=False)
