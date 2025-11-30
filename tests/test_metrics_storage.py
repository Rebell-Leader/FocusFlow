"""
Tests for MetricsTracker storage backends (SQLite and In-Memory).
"""
import pytest
import os
from datetime import datetime
from metrics import MetricsTracker

class TestMetricsTrackerStorage:

    def test_in_memory_metrics(self):
        """Test that in-memory metrics work and are non-persistent."""
        # 1. Initialize in-memory
        mt = MetricsTracker(use_memory=True)
        assert mt.use_memory == True

        # 2. Log check
        mt.log_focus_check(1, "Task 1", "On Track", "Good job")

        # 3. Verify history
        history = mt.get_focus_history()
        assert len(history) == 1
        assert history[0]['verdict'] == "On Track"

        # 4. Verify stats
        stats = mt.get_today_stats()
        assert stats['on_track'] == 1
        assert stats['focus_score'] == 100.0

        # 5. Verify non-persistence
        mt2 = MetricsTracker(use_memory=True)
        assert len(mt2.get_focus_history()) == 0

    def test_clear_all_data(self):
        """Test clearing in-memory data."""
        mt = MetricsTracker(use_memory=True)
        mt.log_focus_check(1, "Task 1", "On Track", "Good job")

        assert len(mt.get_focus_history()) == 1

        mt.clear_all_data()

        assert len(mt.get_focus_history()) == 0
        assert mt.get_today_stats()['on_track'] == 0

    def test_sqlite_metrics(self):
        """Test that SQLite metrics work and IS persistent."""
        db_path = "test_metrics.db"
        if os.path.exists(db_path):
            os.remove(db_path)

        # 1. Initialize SQLite
        mt = MetricsTracker(db_path=db_path, use_memory=False)
        assert mt.use_memory == False

        # 2. Log check
        mt.log_focus_check(1, "Task 1", "On Track", "Good job")

        # 3. Verify persistence
        mt2 = MetricsTracker(db_path=db_path, use_memory=False)
        history = mt2.get_focus_history()
        assert len(history) == 1
        assert history[0]['verdict'] == "On Track"

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
