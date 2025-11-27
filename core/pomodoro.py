"""
Pomodoro Timer Logic for FocusFlow.
"""
from typing import Dict, Tuple

class PomodoroTimer:
    def __init__(self):
        self.state = {
            "minutes": 25,
            "seconds": 0,
            "is_running": False,
            "is_work_time": True,
            "total_seconds": 25 * 60
        }

    def format_time(self, total_seconds: int) -> str:
        """Format seconds to MM:SS format."""
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def get_display(self) -> str:
        """Get current Pomodoro display string."""
        time_str = self.format_time(self.state["total_seconds"])
        status_str = "Work Time ⏰" if self.state["is_work_time"] else "Break Time ☕"
        running_indicator = " (Running)" if self.state["is_running"] else ""
        return f"**{time_str}** {status_str}{running_indicator}"

    def start(self) -> str:
        """Start the Pomodoro timer."""
        self.state["is_running"] = True
        return f"▶️ Timer started! {self.get_display()}"

    def pause(self) -> str:
        """Pause the Pomodoro timer."""
        self.state["is_running"] = False
        return f"⏸️ Timer paused. {self.get_display()}"

    def reset(self) -> str:
        """Reset the Pomodoro timer."""
        self.state["is_running"] = False
        self.state["total_seconds"] = 25 * 60
        self.state["minutes"] = 25
        self.state["seconds"] = 0
        self.state["is_work_time"] = True
        return f"🔄 Timer reset. {self.get_display()}"

    def tick(self) -> Tuple[str, bool]:
        """
        Tick the Pomodoro timer.
        Returns:
            Tuple[display_string, should_play_sound]
        """
        if not self.state["is_running"]:
            return self.get_display(), False

        # Decrement timer
        self.state["total_seconds"] -= 1

        should_play_sound = False

        # Check if session complete
        if self.state["total_seconds"] <= 0:
            # Switch between work and break
            self.state["is_work_time"] = not self.state["is_work_time"]
            self.state["total_seconds"] = (25 * 60) if self.state["is_work_time"] else (5 * 60)
            self.state["is_running"] = False  # Auto-pause to get attention
            should_play_sound = True

        return self.get_display(), should_play_sound
