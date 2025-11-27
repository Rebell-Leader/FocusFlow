"""
FocusFlow: AI Accountability Agent with Gradio 5 Interface.
Configurable via environment variables for HuggingFace Spaces or local use.
"""
import gradio as gr
import os
from dotenv import load_dotenv
from storage import TaskManager
from monitor import FileMonitor
from metrics import MetricsTracker
from voice import voice_generator
from linear_client import LinearClient
from core.pomodoro import PomodoroTimer
from core.focus_check import FocusMonitor
from ui.handlers import UIHandlers
from ui.layout import create_app

# Load environment variables
load_dotenv()

# Import MCP tools to register them with Gradio
try:
    import mcp_tools
    MCP_AVAILABLE = True
except Exception as e:
    print(f"⚠️ MCP tools not available: {e}")
    MCP_AVAILABLE = False

# Configuration from environment
LAUNCH_MODE = os.getenv("LAUNCH_MODE", "demo").lower()  # 'demo' or 'local'
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()  # 'openai', 'anthropic', or 'vllm'
MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", "30"))  # seconds

# Initialize Core Components
task_manager = TaskManager()
file_monitor = FileMonitor()
metrics_tracker = MetricsTracker()
linear_client = LinearClient()

# Initialize Logic Modules
focus_monitor = FocusMonitor(task_manager, file_monitor, metrics_tracker, voice_generator)
focus_monitor.set_launch_mode(LAUNCH_MODE)

pomodoro_timer = PomodoroTimer()

# Initialize UI Handlers
ui_handlers = UIHandlers(task_manager, file_monitor, metrics_tracker, focus_monitor, linear_client)

# Create App
app = create_app(ui_handlers, pomodoro_timer, LAUNCH_MODE, AI_PROVIDER, MONITOR_INTERVAL)

if __name__ == "__main__":
    # Enable MCP server if available
    mcp_enabled = os.getenv("ENABLE_MCP", "true").lower() == "true"

    if MCP_AVAILABLE and mcp_enabled:
        print("🔗 MCP Server enabled! Connect via Claude Desktop or other MCP clients.")
        app.launch(server_name="0.0.0.0", server_port=5000, share=False, mcp_server=True)
    else:
        print("📱 Running without MCP integration")
        app.launch(server_name="0.0.0.0", server_port=5000, share=False)
