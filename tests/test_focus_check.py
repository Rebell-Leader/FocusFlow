import unittest
from unittest.mock import MagicMock
from core.focus_check import FocusMonitor

class TestFocusMonitor(unittest.TestCase):
    def setUp(self):
        self.tm = MagicMock()
        self.fm = MagicMock()
        self.mt = MagicMock()
        self.monitor = FocusMonitor(self.tm, self.fm, self.mt)
        self.monitor.set_launch_mode("local")

    def test_check_no_agent(self):
        log, _, _ = self.monitor.run_check()
        self.assertIn("Agent not initialized", log)

    def test_check_on_track(self):
        agent = MagicMock()
        agent.analyze.return_value = {"verdict": "On Track", "message": "Good job"}
        self.monitor.set_agent(agent)

        self.tm.get_active_task.return_value = {"id": 1, "title": "Test"}
        self.fm.get_recent_activity.return_value = []

        log, alert, voice = self.monitor.run_check()
        self.assertIn("On Track", log)
        self.assertIsNone(alert)

    def test_check_distracted(self):
        agent = MagicMock()
        agent.analyze.return_value = {"verdict": "Distracted", "message": "Stop browsing"}
        self.monitor.set_agent(agent)

        self.tm.get_active_task.return_value = {"id": 1, "title": "Test"}

        log, alert, voice = self.monitor.run_check()
        self.assertIn("Distracted", log)
        self.assertIsNotNone(alert)
