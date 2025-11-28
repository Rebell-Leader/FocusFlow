"""
Task Manager with SQLite backend for CRUD operations.
"""
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
import os


class TaskManager:
    """Manages tasks with SQLite persistence."""

    # Strict status enum
    VALID_STATUSES = {"Todo", "In Progress", "Done"}

    def __init__(self, db_path: str = "focusflow.db", use_memory: bool = False):
        """
        Initialize the task manager.

        Args:
            db_path: Path to SQLite database file
            use_memory: If True, use in-memory list instead of SQLite (for Demo/HF Spaces)
        """
        self.db_path = db_path
        self.use_memory = use_memory
        self.memory_tasks = []  # List of dicts for in-memory storage
        self.memory_counter = 0 # Auto-increment ID for in-memory

        if not self.use_memory:
            self._init_db()
        else:
            print("ℹ️ TaskManager initialized in IN-MEMORY mode (non-persistent)")

    def _init_db(self):
        """Create the tasks table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'Todo',
                    estimated_duration TEXT,
                    position INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Database initialization failed: {e}. Falling back to in-memory mode.")
            self.use_memory = True
            self.memory_tasks = []
            self.memory_counter = 0

    def add_task(self, title: str, description: str = "",
                 estimated_duration: str = "", status: str = "Todo") -> int:
        """Add a new task and return its ID."""
        # Validate status
        if status not in self.VALID_STATUSES:
            status = "Todo"

        if self.use_memory:
            self.memory_counter += 1

            # Calculate position
            max_pos = 0
            if self.memory_tasks:
                max_pos = max(t.get('position', 0) for t in self.memory_tasks)
            position = max_pos + 1

            new_task = {
                "id": self.memory_counter,
                "title": title,
                "description": description,
                "status": status,
                "estimated_duration": estimated_duration,
                "position": position,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self.memory_tasks.append(new_task)
            return self.memory_counter

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get max position
        cursor.execute("SELECT MAX(position) FROM tasks")
        result = cursor.fetchone()
        max_pos = result[0] if result and result[0] is not None else 0
        position = max_pos + 1

        cursor.execute("""
            INSERT INTO tasks (title, description, status, estimated_duration, position)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, status, estimated_duration, position))

        task_id = cursor.lastrowid or 0
        conn.commit()
        conn.close()
        return task_id

    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks ordered by position."""
        if self.use_memory:
            return sorted(self.memory_tasks, key=lambda x: x.get('position', 0))

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, description, status, estimated_duration, position
            FROM tasks ORDER BY position
        """)

        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get a specific task by ID."""
        if self.use_memory:
            for task in self.memory_tasks:
                if task['id'] == task_id:
                    return task.copy()
            return None

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, description, status, estimated_duration, position
            FROM tasks WHERE id = ?
        """, (task_id,))

        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_task(self, task_id: int, **kwargs):
        """Update a task's fields with validation."""
        # Validate status if provided
        if 'status' in kwargs and kwargs['status'] not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")

        allowed_fields = ['title', 'description', 'status', 'estimated_duration', 'position']

        if self.use_memory:
            for task in self.memory_tasks:
                if task['id'] == task_id:
                    for key, value in kwargs.items():
                        if key in allowed_fields:
                            task[key] = value
                    task['updated_at'] = datetime.now().isoformat()
                    return
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        values = []

        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)

        if updates:
            values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

        conn.close()

    def delete_task(self, task_id: int):
        """Delete a task by ID."""
        if self.use_memory:
            self.memory_tasks = [t for t in self.memory_tasks if t['id'] != task_id]
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    def reorder_tasks(self, task_ids: List[int]):
        """Reorder tasks based on new order."""
        if self.use_memory:
            # Create a map for O(1) lookup
            task_map = {t['id']: t for t in self.memory_tasks}

            # Update positions based on the input list order
            for position, task_id in enumerate(task_ids, start=1):
                if task_id in task_map:
                    task_map[task_id]['position'] = position
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for position, task_id in enumerate(task_ids, start=1):
            cursor.execute("UPDATE tasks SET position = ? WHERE id = ?", (position, task_id))

        conn.commit()
        conn.close()

    def get_active_task(self) -> Optional[Dict]:
        """Get the task marked as 'In Progress'."""
        if self.use_memory:
            # Filter for In Progress tasks and sort by position
            active_tasks = [t for t in self.memory_tasks if t['status'] == 'In Progress']
            if not active_tasks:
                return None
            # Return the first one (lowest position)
            return sorted(active_tasks, key=lambda x: x.get('position', 0))[0].copy()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, description, status, estimated_duration
            FROM tasks WHERE status = 'In Progress'
            ORDER BY position LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def set_active_task(self, task_id: int) -> bool:
        """Set a task as 'In Progress' and ensure only one task has this status.
        Returns True if successful, False otherwise."""
        if self.use_memory:
            # Check if task exists
            target_task = None
            for t in self.memory_tasks:
                if t['id'] == task_id:
                    target_task = t
                    break

            if not target_task:
                return False

            if target_task['status'] == 'Done':
                return False

            # Reset other In Progress tasks
            for t in self.memory_tasks:
                if t['status'] == 'In Progress':
                    t['status'] = 'Todo'
                    t['updated_at'] = datetime.now().isoformat()

            # Set target task
            target_task['status'] = 'In Progress'
            target_task['updated_at'] = datetime.now().isoformat()
            return True

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if task exists and is not already Done
        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return False

        current_status = result[0]
        if current_status == "Done":
            conn.close()
            return False

        # Enforce single "In Progress" rule: set all current "In Progress" tasks back to "Todo"
        cursor.execute("""
            UPDATE tasks SET status = 'Todo', updated_at = CURRENT_TIMESTAMP
            WHERE status = 'In Progress'
        """)

        # Set the selected task as 'In Progress'
        cursor.execute("""
            UPDATE tasks SET status = 'In Progress', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (task_id,))

        conn.commit()
        conn.close()
        return True

    def clear_all_tasks(self):
        """Clear all tasks from the database."""
        if self.use_memory:
            self.memory_tasks = []
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()
