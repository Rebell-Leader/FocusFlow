"""
MCP (Model Context Protocol) tools and resources for FocusFlow.
Enables LLM assistants like Claude Desktop to interact with FocusFlow.
"""
import gradio as gr
from typing import Dict, List, Optional
from shared import task_manager, metrics_tracker

# Shared instances are imported from shared.py
# This ensures MCP tools interact with the same data as the main app


@gr.mcp.tool()
def add_task(title: str, description: str = "", duration: int = 30) -> str:
    """
    Create a new task in FocusFlow.

    Args:
        title: Task title (required)
        description: Detailed task description (optional)
        duration: Estimated duration in minutes (default: 30)

    Returns:
        Success message with task ID
    """
    try:
        duration_str = f"{duration} min"
        task_id = task_manager.add_task(title, description, duration_str, status="Todo")
        return f"✅ Task created successfully! ID: {task_id}, Title: '{title}', Duration: {duration} min"
    except Exception as e:
        return f"❌ Error creating task: {str(e)}"


@gr.mcp.tool()
def get_current_task() -> str:
    """
    Get the currently active task (marked as 'In Progress').

    Returns:
        Details of the active task or message if no active task
    """
    try:
        active_task = task_manager.get_active_task()
        if not active_task:
            return "ℹ️ No active task. Use start_task(task_id) to begin working on a task."

        return f"""📋 Current Active Task:
- ID: {active_task['id']}
- Title: {active_task['title']}
- Description: {active_task.get('description', 'No description')}
- Duration: {active_task.get('estimated_duration', 'Not specified')}
- Status: {active_task['status']}"""
    except Exception as e:
        return f"❌ Error getting current task: {str(e)}"


@gr.mcp.tool()
def start_task(task_id: int) -> str:
    """
    Mark a task as 'In Progress' and set it as the active task.
    Only one task can be active at a time.

    Args:
        task_id: ID of the task to start

    Returns:
        Success or error message
    """
    try:
        # Check if task exists first
        task = task_manager.get_task(task_id)
        if not task:
            return f"❌ Task {task_id} not found. Use get_all_tasks() to see available tasks."

        success = task_manager.set_active_task(task_id)
        if success:
            return f"✅ Task {task_id} started: '{task['title']}'. FocusFlow is now monitoring your progress!"
        else:
            return f"❌ Failed to start task {task_id}. Task is already marked as Done."
    except Exception as e:
        return f"❌ Error starting task: {str(e)}"


@gr.mcp.tool()
def mark_task_done(task_id: int) -> str:
    """
    Mark a task as completed ('Done').

    Args:
        task_id: ID of the task to complete

    Returns:
        Success or error message
    """
    try:
        # Check if task exists first
        task = task_manager.get_task(task_id)
        if not task:
            return f"❌ Task {task_id} not found. Use get_all_tasks() to see available tasks."

        task_manager.update_task(task_id, status="Done")
        return f"🎉 Task {task_id} completed: '{task['title']}'! Great work!"
    except Exception as e:
        return f"❌ Error marking task done: {str(e)}"


@gr.mcp.tool()
def get_all_tasks() -> str:
    """
    Get a list of all tasks with their current status.

    Returns:
        Formatted list of all tasks
    """
    try:
        tasks = task_manager.get_all_tasks()
        if not tasks:
            return "📝 No tasks yet. Use add_task() to create your first task!"

        result = f"📋 All Tasks ({len(tasks)} total):\n\n"
        for task in tasks:
            status_emoji = "✅" if task['status'] == "Done" else "🔄" if task['status'] == "In Progress" else "⏳"
            result += f"{status_emoji} [{task['id']}] {task['title']}\n"
            if task.get('description'):
                result += f"   Description: {task['description']}\n"
            result += f"   Status: {task['status']} | Duration: {task.get('estimated_duration', 'N/A')}\n\n"

        return result.strip()
    except Exception as e:
        return f"❌ Error getting tasks: {str(e)}"


@gr.mcp.tool()
def delete_task(task_id: int) -> str:
    """
    Delete a task permanently.

    Args:
        task_id: ID of the task to delete

    Returns:
        Success or error message
    """
    try:
        task = task_manager.get_task(task_id)
        if not task:
            return f"❌ Task {task_id} not found."

        title = task['title']
        task_manager.delete_task(task_id)
        return f"🗑️ Task {task_id} deleted: '{title}'"
    except Exception as e:
        return f"❌ Error deleting task: {str(e)}"


@gr.mcp.tool()
def update_task(task_id: int, title: Optional[str] = None, description: Optional[str] = None,
                status: Optional[str] = None, duration: Optional[int] = None) -> str:
    """
    Update an existing task.

    Args:
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        status: New status (Todo, In Progress, Done) (optional)
        duration: New estimated duration in minutes (optional)

    Returns:
        Success or error message
    """
    try:
        task = task_manager.get_task(task_id)
        if not task:
            return f"❌ Task {task_id} not found."

        updates = {}
        if title is not None:
            updates['title'] = title
        if description is not None:
            updates['description'] = description
        if status is not None:
            updates['status'] = status
        if duration is not None:
            updates['estimated_duration'] = f"{duration} min"

        if not updates:
            return "ℹ️ No changes provided."

        task_manager.update_task(task_id, **updates)
        return f"✅ Task {task_id} updated successfully!"
    except Exception as e:
        return f"❌ Error updating task: {str(e)}"


@gr.mcp.tool()
def get_productivity_stats() -> str:
    """
    Get productivity statistics and insights including focus metrics.

    Returns:
        Summary of task completion, progress, and focus scores
    """
    try:
        # Task statistics
        tasks = task_manager.get_all_tasks()
        if not tasks:
            return "📊 No tasks to analyze yet. Create some tasks to see your productivity stats!"

        total = len(tasks)
        completed = sum(1 for t in tasks if t['status'] == 'Done')
        in_progress = sum(1 for t in tasks if t['status'] == 'In Progress')
        todo = sum(1 for t in tasks if t['status'] == 'Todo')

        completion_rate = (completed / total * 100) if total > 0 else 0

        # Focus metrics
        today_stats = metrics_tracker.get_today_stats()
        current_streak = metrics_tracker.get_current_streak()

        result = f"""📊 Productivity Statistics:

📋 Task Progress:
✅ Completed: {completed}/{total} tasks ({completion_rate:.1f}%)
🔄 In Progress: {in_progress} task(s)
⏳ To Do: {todo} tasks

🎯 Focus Metrics (Today):
⭐ Focus Score: {today_stats['focus_score']}/100
🔥 Current Streak: {current_streak} consecutive "On Track" checks
📊 Total Checks: {today_stats['total_checks']}
  • On Track: {today_stats['on_track']}
  • Distracted: {today_stats['distracted']}
  • Idle: {today_stats['idle']}

Keep up the good work! 🎯"""
        return result
    except Exception as e:
        return f"❌ Error getting stats: {str(e)}"


# MCP Resources
@gr.mcp.resource("focusflow://tasks/all")
def get_all_tasks_resource() -> str:
    """Expose all tasks as an MCP resource."""
    return get_all_tasks()


@gr.mcp.resource("focusflow://tasks/active")
def get_active_task_resource() -> str:
    """Expose the active task as an MCP resource."""
    return get_current_task()


@gr.mcp.resource("focusflow://stats")
def get_stats_resource() -> str:
    """Expose productivity statistics as an MCP resource."""
    return get_productivity_stats()
