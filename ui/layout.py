"""
Gradio Layout for FocusFlow.
"""
import gradio as gr
import os
import inspect
from core.pomodoro import PomodoroTimer
import mcp_tools

def register_tool_safely(func):
    """Register a tool with correct signature by creating dummy components."""
    sig = inspect.signature(func)
    inputs = []
    for name, param in sig.parameters.items():
        # Map types to components
        if param.annotation == int:
            inputs.append(gr.Number(label=name, visible=False))
        elif param.annotation == bool:
            inputs.append(gr.Checkbox(label=name, visible=False))
        else:
            inputs.append(gr.Textbox(label=name, visible=False))

    # Dummy output to capture return value
    output = gr.Textbox(visible=False)

    # Hidden button to trigger
    btn = gr.Button(f"cmd_{func.__name__}", visible=False)
    btn.click(fn=func, inputs=inputs, outputs=[output])

def create_app(ui_handlers, pomodoro_timer: PomodoroTimer, launch_mode: str, ai_provider: str, monitor_interval: int):
    """Create the Gradio Blocks app."""

    with gr.Blocks(title="FocusFlow AI") as app:

        # MCP Tools Registration (Hidden)
        with gr.Row(visible=False):
            # Register all tools from mcp_tools
            register_tool_safely(mcp_tools.add_task)
            register_tool_safely(mcp_tools.get_current_task)
            register_tool_safely(mcp_tools.start_task)
            register_tool_safely(mcp_tools.mark_task_done)
            register_tool_safely(mcp_tools.get_all_tasks)
            register_tool_safely(mcp_tools.delete_task)
            register_tool_safely(mcp_tools.update_task)
            register_tool_safely(mcp_tools.get_productivity_stats)

        # Hidden component for browser alerts
        alert_trigger = gr.HTML(visible=False)

        # Auto-refresh timer for monitoring (default 30s)
        monitor_timer = gr.Timer(value=monitor_interval, active=False)

        # Dedicated 1-second timer for Pomodoro
        pomodoro_ticker = gr.Timer(value=1, active=True)

        with gr.Tabs() as tabs:
            # Tab 1: Home/Landing Page
            with gr.Tab("🏠 Home"):
                gr.Markdown("""
                # 🦉 FocusFlow - Your AI Accountability Buddy

                Keep focused on your coding tasks with Duolingo-style nudges!
                """)

                # Status indicators
                init_status = gr.Textbox(label="AI Status", value="Initializing...", interactive=False, scale=1)
                voice_status_display = gr.Textbox(label="Voice Status", value="Checking...", interactive=False, scale=1)

                gr.Markdown("""
                ## ✨ Features

                - **🎯 AI-Powered Project Planning**: Break down projects into actionable micro-tasks
                - **📊 Progress Tracking**: Visual progress monitoring with completion percentages
                - **👁️ Real-Time Monitoring**: Track your coding activity and stay focused
                - **🦉 Duolingo-Style Nudges**: Encouraging, sassy, and gentle reminders
                - **🔔 Browser Notifications**: Get alerted when you're distracted
                - **🚀 Multi-Provider AI**: OpenAI, Anthropic, or local vLLM support
                - **🔊 Voice Feedback**: ElevenLabs voice alerts for maximum engagement

                ## ⚙️ Current Configuration
                """)

                # Dynamic AI provider display
                ai_provider_display = gr.Markdown(f"**AI Provider:** `{ai_provider.upper()}`")

                with gr.Row():
                    gr.Markdown(f"**Mode:** `{launch_mode.upper()}`")
                    ai_provider_display
                    gr.Markdown(f"**Check Interval:** `{monitor_interval}s`")

                if launch_mode == "demo":
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
                onboard_status = gr.Markdown("")

                # Linear Integration
                gr.Markdown("""
                ---
                ## 🔗 Import from Linear
                Connect to your Linear workspace to import existing issues.
                """)

                with gr.Row():
                    refresh_projects_btn = gr.Button("🔄 Load Projects", size="sm", scale=1)
                    project_selector = gr.Dropdown(label="Select Project", choices=[], scale=3, interactive=True)
                    import_linear_btn = gr.Button("⬇️ Import Tasks", variant="secondary", scale=1)

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

                # State to hold selected task ID
                selected_task_id = gr.State(value=None)

                # Table view
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

                # Single dynamic form (hidden by default)
                with gr.Column(visible=False, elem_id="task-form-container") as task_form:
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

            # Tab 4: Dashboard
            with gr.Tab("📊 Dashboard"):
                gr.Markdown("## 📊 Productivity Dashboard")

                # Today's stats
                with gr.Row():
                    with gr.Column(scale=1):
                        today_focus_score = gr.Number(label="Focus Score", value=0, interactive=False)
                    with gr.Column(scale=1):
                        today_streak = gr.Number(label="Current Streak 🔥", value=0, interactive=False)
                    with gr.Column(scale=1):
                        today_checks = gr.Number(label="Total Checks", value=0, interactive=False)

                # State distribution (today)
                gr.Markdown("### Today's Focus Distribution")
                import pandas as pd
                empty_state_df = pd.DataFrame([{"state": "On Track", "count": 0}, {"state": "Distracted", "count": 0}, {"state": "Idle", "count": 0}])
                state_plot = gr.BarPlot(
                    value=empty_state_df,
                    x="state",
                    y="count",
                    title="Focus States Distribution"
                )

                # Weekly focus score trend
                gr.Markdown("### Weekly Focus Score Trend")
                empty_weekly_df = pd.DataFrame({"date": [], "score": []})
                weekly_plot = gr.LinePlot(
                    value=empty_weekly_df,
                    x="date",
                    y="score",
                    title="Focus Score (Last 7 Days)"
                )

                refresh_dashboard_btn = gr.Button("🔄 Refresh Dashboard", variant="secondary")

            # Tab 5: Monitor
            with gr.Tab("👁️ Monitor"):
                gr.Markdown("## Focus Monitoring")

                # Mode-specific UI
                if launch_mode == "demo":
                    gr.Markdown("**Demo Workspace** - Edit the text below to simulate coding:")
                    demo_textarea = gr.Textbox(
                        label="Your Code",
                        placeholder="Type or paste your code here...",
                        lines=8,
                        value="# Welcome to FocusFlow!\n# Start coding..."
                    )
                    demo_update_btn = gr.Button("💾 Save Changes", variant="secondary")
                    demo_status = gr.Textbox(label="Status", interactive=False)
                    watch_path_input = gr.State(value=None) # Dummy
                    start_monitor_btn = gr.State(value=None) # Dummy
                    stop_monitor_btn = gr.State(value=None) # Dummy
                    monitor_status = gr.State(value=None) # Dummy
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
                    demo_textarea = gr.State(value=None) # Dummy
                    demo_update_btn = gr.State(value=None) # Dummy
                    demo_status = gr.State(value=None) # Dummy

                # Check frequency selector
                gr.Markdown("### ⚙️ Monitoring Settings")
                check_frequency = gr.Dropdown(
                    label="Check Frequency",
                    choices=["30 seconds", "1 minute", "5 minutes", "10 minutes"],
                    value="30 seconds",
                    interactive=True
                )

                check_frequency.change(
                    fn=ui_handlers.set_check_interval,
                    inputs=[check_frequency],
                    outputs=[monitor_timer, monitor_status if launch_mode != "demo" else demo_status],
                    api_name=False
                )

                # Pomodoro Timer
                gr.Markdown("### 🍅 Pomodoro Timer")

                # Timer display with embedded audio alerts
                with gr.Row():
                    pomodoro_display = gr.Markdown(value=pomodoro_timer.get_display(), elem_id="pomodoro-display")
                    gr.HTML("""
                    <audio id="pomodoro-alert" preload="auto">
                        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTUI" type="audio/wav">
                    </audio>
                    <audio id="nudge-alert" preload="auto">
                        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTUI" type="audio/wav">
                    </audio>
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

                # Voice feedback player
                voice_audio = gr.Audio(
                    label="🔊 Voice Feedback",
                    visible=True,
                    autoplay=True,
                    show_label=True,
                    elem_id="voice-feedback-player"
                )

                with gr.Row():
                    manual_check_btn = gr.Button("🔍 Run Focus Check Now", variant="secondary")
                    if launch_mode == "demo":
                        timer_toggle_btn = gr.Button("⏸️ Pause Auto-Check", variant="secondary")
                    else:
                        timer_toggle_btn = gr.Button("▶️ Start Auto-Check", variant="secondary")

        # --- Event Handlers ---

        # Initialization
        app.load(fn=lambda: ui_handlers.initialize_agent(ai_provider), outputs=[init_status, ai_provider_display], api_name=False)
        app.load(fn=ui_handlers.get_voice_status_ui, outputs=voice_status_display, api_name=False)

        # Onboarding
        generate_btn.click(
            fn=ui_handlers.process_onboarding,
            inputs=[project_input],
            outputs=[onboard_status, task_table, progress_bar],
            api_name=False
        )

        # Linear Integration
        refresh_projects_btn.click(
            fn=ui_handlers.get_linear_projects_ui,
            outputs=[project_selector, onboard_status],
            api_name=False
        )
        import_linear_btn.click(
            fn=ui_handlers.import_linear_tasks_ui,
            inputs=[project_selector],
            outputs=[onboard_status, task_table, progress_bar],
            api_name=False
        )

        # Task Management
        add_task_trigger_btn.click(
            fn=lambda: gr.update(visible=True),
            outputs=task_form,
            api_name=False
        )
        form_cancel_btn.click(
            fn=lambda: gr.update(visible=False),
            outputs=task_form,
            api_name=False
        )
        form_save_btn.click(
            fn=ui_handlers.add_new_task,
            inputs=[form_title, form_desc, form_duration, form_status],
            outputs=[form_title, form_desc, form_duration, form_status, task_table, progress_bar],
            api_name=False
        )
        form_save_btn.click(
            fn=lambda: gr.update(visible=False),
            outputs=task_form,
            api_name=False
        )

        # Task Selection Handler
        def on_select_task(evt: gr.SelectData, data):
            try:
                # data is a pandas DataFrame
                row_index = evt.index[0]
                task_id = data.iloc[row_index][0] # ID is in first column
                return task_id, f"✅ Selected Task ID: {task_id}"
            except Exception as e:
                return None, f"❌ Error selecting task: {str(e)}"

        task_table.select(
            fn=on_select_task,
            inputs=[task_table],
            outputs=[selected_task_id, selection_info],
            api_name=False
        )

        # Button Handlers
        start_task_btn.click(
            fn=ui_handlers.set_task_active,
            inputs=[selected_task_id],
            outputs=[onboard_status, task_table, progress_bar],
            api_name=False
        )

        mark_done_btn.click(
            fn=ui_handlers.mark_task_done,
            inputs=[selected_task_id],
            outputs=[onboard_status, task_table, progress_bar],
            api_name=False
        )

        delete_task_btn.click(
            fn=ui_handlers.delete_task,
            inputs=[selected_task_id],
            outputs=[onboard_status, task_table, progress_bar],
            api_name=False
        )

        # Monitoring
        if launch_mode == "demo":
            demo_update_btn.click(
                fn=ui_handlers.focus_monitor.update_demo_text,
                inputs=[demo_textarea],
                outputs=[demo_status],
                api_name=False
            )
            # Auto-activate timer in demo mode
            app.load(fn=lambda: gr.update(active=True), outputs=monitor_timer, api_name=False)

            # Toggle handler for demo mode
            def toggle_demo_timer(active):
                new_state = not active
                btn_label = "▶️ Start Auto-Check" if active else "⏸️ Pause Auto-Check"
                return gr.update(active=new_state), gr.update(value=btn_label), new_state

            # We need a state to track timer status for the button label
            timer_active_state = gr.State(value=True)

            timer_toggle_btn.click(
                fn=toggle_demo_timer,
                inputs=[timer_active_state],
                outputs=[monitor_timer, timer_toggle_btn, timer_active_state],
                api_name=False
            )

        else:
            start_monitor_btn.click(
                fn=lambda p: ui_handlers.start_monitoring(p, launch_mode),
                inputs=[watch_path_input],
                outputs=[monitor_status, monitor_timer],
                api_name=False
            )
            stop_monitor_btn.click(
                fn=ui_handlers.stop_monitoring,
                outputs=[monitor_status, monitor_timer],
                api_name=False
            )

            # Toggle handler for local mode (if needed, but local mode uses start/stop buttons)
            # The button is present in local mode too: "Start Auto-Check"
            # But local mode logic is tied to file monitoring start/stop.
            # Let's map it to start/stop monitoring if it's the same intention,
            # or just pause the timer while keeping monitoring active?
            # Given the button label "Start Auto-Check", it seems redundant with "Start" button in Monitor tab.
            # But let's make it toggle the timer.

            def toggle_local_timer(active):
                new_state = not active
                btn_label = "▶️ Start Auto-Check" if active else "⏸️ Pause Auto-Check"
                return gr.update(active=new_state), gr.update(value=btn_label), new_state

            timer_active_state = gr.State(value=False)

            timer_toggle_btn.click(
                fn=toggle_local_timer,
                inputs=[timer_active_state],
                outputs=[monitor_timer, timer_toggle_btn, timer_active_state],
                api_name=False
            )


        # Pomodoro Handlers
        pomodoro_start_btn.click(fn=pomodoro_timer.start, outputs=pomodoro_display, api_name=False)
        pomodoro_stop_btn.click(fn=pomodoro_timer.pause, outputs=pomodoro_display, api_name=False)
        pomodoro_reset_btn.click(fn=pomodoro_timer.reset, outputs=pomodoro_display, api_name=False)

        # Pomodoro Tick (1 second)
        pomodoro_ticker.tick(fn=pomodoro_timer.tick, outputs=[pomodoro_display, alert_trigger])
        # Note: tick returns (display, should_play_sound).
        # But alert_trigger is HTML. I need a wrapper.

        def pomodoro_tick_wrapper():
            display, play_sound = pomodoro_timer.tick()
            js = ""
            if play_sound:
                js = """
                <script>
                (function() {
                    const audio = document.getElementById('pomodoro-alert');
                    if (audio) { audio.play(); }
                })();
                </script>
                """
            return display, js

        pomodoro_ticker.tick(fn=pomodoro_tick_wrapper, outputs=[pomodoro_display, alert_trigger], api_name=False)

        # Focus Check Tick (Monitor Interval)
        def monitor_tick_wrapper():
            focus_result, alert_js, voice_data = ui_handlers.focus_monitor.run_check()
            alert_html = f'<script>{alert_js}</script>' if alert_js else ""
            voice_update = gr.update(visible=True, value=voice_data) if voice_data else gr.update(visible=False)
            return focus_result, alert_html, voice_update

        monitor_timer.tick(
            fn=monitor_tick_wrapper,
            outputs=[focus_log, alert_trigger, voice_audio],
            api_name=False
        )

        manual_check_btn.click(
            fn=monitor_tick_wrapper,
            outputs=[focus_log, alert_trigger, voice_audio],
            api_name=False
        )

        # Dashboard
        refresh_dashboard_btn.click(
            fn=ui_handlers.refresh_dashboard,
            outputs=[today_focus_score, today_streak, today_checks, state_plot, weekly_plot],
            api_name=False
        )
        app.load(
            fn=ui_handlers.refresh_dashboard,
            outputs=[today_focus_score, today_streak, today_checks, state_plot, weekly_plot],
            api_name=False
        )

    return app
