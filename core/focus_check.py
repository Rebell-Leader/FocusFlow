"""
Focus Monitoring Logic.
"""
import time
import json
from typing import List, Optional, Tuple, Any

class FocusMonitor:
    def __init__(self, task_manager, file_monitor, metrics_tracker, voice_generator=None):
        self.task_manager = task_manager
        self.file_monitor = file_monitor
        self.metrics_tracker = metrics_tracker
        self.voice_generator = voice_generator

        self.focus_agent = None
        self.consecutive_distracted = 0
        self.activity_log: List[str] = []
        self.demo_text_content = ""
        self.launch_mode = "demo" # Default

    def set_agent(self, agent):
        self.focus_agent = agent

    def set_launch_mode(self, mode: str):
        self.launch_mode = mode

    def update_demo_text(self, text: str) -> str:
        """Update demo text content (demo mode only)."""
        self.demo_text_content = text
        return f"✅ Text updated ({len(text)} characters)"

    def get_activity_summary(self, monitoring_active: bool) -> str:
        """Get recent activity summary."""
        if self.launch_mode == "demo":
            return f"📝 Demo text content: {len(self.demo_text_content)} characters"

        if not monitoring_active:
            return "⏸️ Monitoring is not active"

        recent = self.file_monitor.get_recent_activity(5)
        if not recent:
            return "💤 No recent file activity"

        summary = []
        for event in recent:
            summary.append(f"• {event['type'].upper()}: {event['filename']}")

        return "\n".join(summary)

    def run_check(self) -> Tuple[str, Optional[str], Optional[Any]]:
        """
        Run the focus check analysis with distraction escalation.
        Returns:
            Tuple[log_string, alert_js, voice_audio]
        """
        if not self.focus_agent:
            return "⚠️ Agent not initialized. Check environment variables.", None, None

        active_task = self.task_manager.get_active_task()

        # Get recent activity based on mode
        if self.launch_mode == "demo":
            # In demo mode, create synthetic activity from text content
            recent_activity = [{
                'type': 'text_edit',
                'filename': 'demo_workspace',
                'content': self.demo_text_content[-500:] if self.demo_text_content else "",
                'timestamp': time.time()
            }] if self.demo_text_content else []
        else:
            recent_activity = self.file_monitor.get_recent_activity(10)

        result = self.focus_agent.analyze(active_task, recent_activity)

        verdict = result.get("verdict", "Unknown")
        message = result.get("message", "No message")

        # Handle distraction escalation logic
        if verdict == "On Track":
            # Reset counter when back on track
            self.consecutive_distracted = 0
        elif verdict == "Distracted":
            # Increment distraction counter
            self.consecutive_distracted += 1

        # Log to metrics if we have an active task
        if active_task:
            self.metrics_tracker.log_focus_check(
                active_task['id'],
                active_task['title'],
                verdict,
                message
            )

        # Determine emoji
        emoji = "✅" if verdict == "On Track" else "⚠️" if verdict == "Distracted" else "💤"

        log_entry = f"{emoji} [{verdict}] {message}"
        self.activity_log.append(log_entry)

        # Keep only last 20 entries
        if len(self.activity_log) > 20:
            self.activity_log.pop(0)

        # Generate voice feedback (optional, graceful if unavailable)
        voice_audio = None
        if self.voice_generator:
            try:
                voice_audio = self.voice_generator.get_focus_message_audio(verdict, message)
            except Exception as e:
                print(f"Voice generation error: {e}")

        # Trigger browser alert and audio for distracted/idle status with escalation
        alert_js = None
        if verdict in ["Distracted", "Idle"]:
            safe_message = json.dumps(message)

            # Escalation logic:
            # 1st distraction: play sound only
            # 2nd distraction: play sound again
            # 3rd+ distraction: add voice feedback
            # play_voice = self.consecutive_distracted >= 3 # Logic handled by caller or voice_audio presence?
            # Actually voice_audio is generated regardless, but maybe we only play it if distracted?
            # The original code generated it always if available.

            alert_js = f"""
            () => {{
                const audio = document.getElementById('nudge-alert');
                if (audio) {{
                    audio.currentTime = 0;
                    audio.play().catch(e => console.log('Audio play failed:', e));
                }}
                if (Notification.permission === "granted") {{
                    new Notification("FocusFlow Alert 🦉", {{
                        body: {safe_message},
                        icon: "https://em-content.zobj.net/thumbs/160/apple/354/owl_1f989.png"
                    }});
                }}
                return null;
            }}
            """

        return "\n".join(self.activity_log), alert_js, voice_audio
