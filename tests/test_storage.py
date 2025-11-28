"""
Tests for TaskManager storage backends (SQLite and In-Memory).
"""
import pytest
import os
from storage import TaskManager

class TestTaskManagerStorage:

    def test_in_memory_storage(self):
        """Test that in-memory storage works and is non-persistent."""
        # 1. Initialize in-memory
        tm = TaskManager(use_memory=True)
        assert tm.use_memory == True

        # 2. Add task
        task_id = tm.add_task("Memory Task", "Description")
        assert task_id == 1

        # 3. Retrieve task
        task = tm.get_task(task_id)
        assert task['title'] == "Memory Task"

        # 4. Update task
        tm.update_task(task_id, status="In Progress")
        task = tm.get_task(task_id)
        assert task['status'] == "In Progress"

        # 5. Verify non-persistence (new instance should be empty)
        tm2 = TaskManager(use_memory=True)
        assert len(tm2.get_all_tasks()) == 0

    def test_sqlite_storage(self):
        """Test that SQLite storage works and IS persistent."""
        db_path = "test_focusflow.db"
        if os.path.exists(db_path):
            os.remove(db_path)

        # 1. Initialize SQLite
        tm = TaskManager(db_path=db_path, use_memory=False)
        assert tm.use_memory == False

        # 2. Add task
        task_id = tm.add_task("SQLite Task", "Description")

        # 3. Verify persistence (new instance should see the task)
        tm2 = TaskManager(db_path=db_path, use_memory=False)
        tasks = tm2.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0]['title'] == "SQLite Task"

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_active_task_logic_memory(self):
        """Test active task logic in memory mode."""
        tm = TaskManager(use_memory=True)
        t1 = tm.add_task("Task 1")
        t2 = tm.add_task("Task 2")

        # Set t1 active
        tm.set_active_task(t1)
        active = tm.get_active_task()
        assert active['id'] == t1

        # Set t2 active (should unset t1)
        tm.set_active_task(t2)
        active = tm.get_active_task()
        assert active['id'] == t2

        t1_data = tm.get_task(t1)
        assert t1_data['status'] == 'Todo'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
