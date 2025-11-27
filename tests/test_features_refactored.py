"""
Comprehensive autotests for FocusFlow features (Refactored):
- Check frequency configuration
- Distraction escalation logic
- Pomodoro timer functionality
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import new modules
from core.pomodoro import PomodoroTimer
from core.focus_check import FocusMonitor
from ui.handlers import UIHandlers
from agent import FocusAgent, MockFocusAgent
from storage import TaskManager

class TestCheckFrequency:
    """Test check frequency configuration and updates."""

    def setup_method(self):
        self.tm = MagicMock()
        self.fm = MagicMock()
        self.mt = MagicMock()
        self.fmon = MagicMock()
        self.handlers = UIHandlers(self.tm, self.fm, self.mt, self.fmon)

    def test_check_frequency_options_exist(self):
        """Verify check frequency dropdown has all required options."""
        pass

    def test_check_frequency_parsing(self):
        """Test converting dropdown values to seconds."""
        test_cases = {
            "30 seconds": 30,
            "1 minute": 60,
            "5 minutes": 300,
            "10 minutes": 600,
        }
        for label, expected_seconds in test_cases.items():
            timer, msg = self.handlers.set_check_interval(label)
            assert timer.value == expected_seconds
            assert self.handlers.check_interval == expected_seconds

class TestDistractionEscalation:
    """Test distraction escalation logic (sound -> sound -> voice)."""

    def setup_method(self):
        self.tm = MagicMock()
        self.fm = MagicMock()
        self.mt = MagicMock()
        self.monitor = FocusMonitor(self.tm, self.fm, self.mt)
        self.monitor.set_launch_mode("local")
        # Mock agent
        self.agent = MagicMock()
        self.monitor.set_agent(self.agent)
        self.tm.get_active_task.return_value = {"id": 1, "title": "Test"}
        self.fm.get_recent_activity.return_value = []

    def test_escalation_counter_increments_on_distracted(self):
        """Verify consecutive_distracted increments on 'Distracted' verdict."""
        self.monitor.consecutive_distracted = 0
        self.agent.analyze.return_value = {"verdict": "Distracted", "message": "msg"}

        # 1st
        self.monitor.run_check()
        assert self.monitor.consecutive_distracted == 1

        # 2nd
        self.monitor.run_check()
        assert self.monitor.consecutive_distracted == 2

        # 3rd
        self.monitor.run_check()
        assert self.monitor.consecutive_distracted == 3

    def test_escalation_counter_resets_on_track(self):
        """Verify counter resets to 0 when verdict is 'On Track'."""
        self.monitor.consecutive_distracted = 3
        self.agent.analyze.return_value = {"verdict": "On Track", "message": "msg"}

        self.monitor.run_check()
        assert self.monitor.consecutive_distracted == 0

    def test_activity_log_entry_added(self):
        """Verify log entries are added correctly."""
        self.agent.analyze.return_value = {"verdict": "On Track", "message": "Great work!"}
        self.monitor.run_check()
        assert any("Great work!" in entry for entry in self.monitor.activity_log)
        assert len(self.monitor.activity_log) == 1

    def test_activity_log_maintains_max_20_entries(self):
        """Verify activity log maintains maximum 20 entries."""
        # Start with 20 entries
        self.monitor.activity_log = [f"Entry {i}" for i in range(20)]
        self.agent.analyze.return_value = {"verdict": "On Track", "message": "New"}

        self.monitor.run_check()

        # Should still be 20 (20 + 1 - 1)
        assert len(self.monitor.activity_log) == 20
        assert "Entry 0" not in self.monitor.activity_log
        assert any("New" in x for x in self.monitor.activity_log)


class TestPomodoroTimerRefactored:
    """Test Pomodoro timer state management."""

    def setup_method(self):
        self.timer = PomodoroTimer()

    def test_pomodoro_initial_state(self):
        assert self.timer.state["total_seconds"] == 1500
        assert self.timer.state["is_work_time"] == True
        assert self.timer.state["is_running"] == False

    def test_pomodoro_format_time(self):
        assert self.timer.format_time(1500) == "25:00"
        assert self.timer.format_time(0) == "00:00"
        assert self.timer.format_time(125) == "02:05"

    def test_pomodoro_start(self):
        result = self.timer.start()
        assert self.timer.state["is_running"] == True
        assert "▶️" in result

    def test_pomodoro_pause(self):
        self.timer.start()
        result = self.timer.pause()
        assert self.timer.state["is_running"] == False
        assert "⏸️" in result

    def test_pomodoro_reset(self):
        self.timer.state["total_seconds"] = 500
        result = self.timer.reset()
        assert self.timer.state["total_seconds"] == 1500
        assert "🔄" in result

    def test_pomodoro_tick_decrements(self):
        self.timer.start()
        self.timer.state["total_seconds"] = 100
        self.timer.tick()
        assert self.timer.state["total_seconds"] == 99

    def test_pomodoro_tick_when_paused(self):
        self.timer.pause()
        self.timer.state["total_seconds"] = 100
        self.timer.tick()
        assert self.timer.state["total_seconds"] == 100

class TestMockAgentRefactored:
    def test_mock_agent_initialization(self):
        agent = MockFocusAgent()
        assert agent.provider == "mock"
        assert agent.connection_healthy == True

class TestTaskManagerRefactored:
    def test_task_manager_initialization(self):
        tm = TaskManager()
        assert isinstance(tm, TaskManager)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
