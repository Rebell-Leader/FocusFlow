import unittest
from core.pomodoro import PomodoroTimer

class TestPomodoroTimer(unittest.TestCase):
    def setUp(self):
        self.timer = PomodoroTimer()

    def test_initial_state(self):
        self.assertEqual(self.timer.state["minutes"], 25)
        self.assertFalse(self.timer.state["is_running"])

    def test_start_pause_reset(self):
        self.timer.start()
        self.assertTrue(self.timer.state["is_running"])
        self.timer.pause()
        self.assertFalse(self.timer.state["is_running"])
        self.timer.reset()
        self.assertEqual(self.timer.state["total_seconds"], 25 * 60)

    def test_tick(self):
        self.timer.start()
        display, sound = self.timer.tick()
        self.assertEqual(self.timer.state["total_seconds"], 25 * 60 - 1)
        self.assertFalse(sound)

    def test_session_complete(self):
        self.timer.start()
        self.timer.state["total_seconds"] = 1
        display, sound = self.timer.tick()
        self.assertTrue(sound)
        self.assertFalse(self.timer.state["is_running"])
        self.assertFalse(self.timer.state["is_work_time"]) # Switched to break
