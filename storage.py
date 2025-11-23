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
    
    def __init__(self, db_path: str = "focusflow.db"):
        """Initialize the task manager with SQLite database."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create the tasks table if it doesn't exist."""
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
    
    def add_task(self, title: str, description: str = "", 
                 estimated_duration: str = "", status: str = "Todo") -> int:
        """Add a new task and return its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get max position
        cursor.execute("SELECT MAX(position) FROM tasks")
        max_pos = cursor.fetchone()[0]
        position = (max_pos or 0) + 1
        
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
        """Update a task's fields."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        allowed_fields = ['title', 'description', 'status', 'estimated_duration', 'position']
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
    
    def reorder_tasks(self, task_ids: List[int]):
        """Reorder tasks based on new order."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for position, task_id in enumerate(task_ids, start=1):
            cursor.execute("UPDATE tasks SET position = ? WHERE id = ?", (position, task_id))
        
        conn.commit()
        conn.close()
    
    def get_active_task(self) -> Optional[Dict]:
        """Get the task marked as 'In Progress'."""
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
    
    def set_active_task(self, task_id: int):
        """Set a task as 'In Progress' and mark others as 'Todo' or 'Done'."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First, set all 'In Progress' tasks back to 'Todo' (except done ones)
        cursor.execute("""
            UPDATE tasks SET status = 'Todo' 
            WHERE status = 'In Progress'
        """)
        
        # Set the selected task as 'In Progress'
        cursor.execute("""
            UPDATE tasks SET status = 'In Progress' 
            WHERE id = ?
        """, (task_id,))
        
        conn.commit()
        conn.close()
    
    def clear_all_tasks(self):
        """Clear all tasks from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()
