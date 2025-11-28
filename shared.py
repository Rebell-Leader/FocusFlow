"""
Shared module to hold singleton instances.
Ensures app.py and mcp_tools.py share the same state.
"""
from storage import TaskManager
from metrics import MetricsTracker
import os

# Configuration
LAUNCH_MODE = os.getenv("LAUNCH_MODE", "demo").lower()

# Initialize singletons
# For demo mode, we use in-memory storage to avoid filesystem issues in HF Spaces
use_memory = (LAUNCH_MODE == "demo")

task_manager = TaskManager(use_memory=use_memory)
metrics_tracker = MetricsTracker()
