"""
ElevenLabs Voice Integration for FocusFlow.
Provides optional voice feedback for focus agent and Pomodoro timer.
Gracefully falls back to text-only mode if API key is missing or quota exceeded.
"""
import os
import tempfile
from typing import Optional, Dict
from pathlib import Path


class VoiceGenerator:
    """
    Handles text-to-speech generation using ElevenLabs API.
    Designed for graceful degradation - never crashes if voice unavailable.
    """

    def __init__(self):
        """Initialize ElevenLabs client if API key available."""
        self.initialize()

    def initialize(self):
        """Initialize or re-initialize the client."""
        self.client = None
        self.available = False
        self.voice_id = "JBFqnCBsd6RMkjVDRZzb"  # George - friendly, clear voice
        self.model_id = "eleven_turbo_v2_5"  # Fast, low-latency model

        try:
            # Check for API key (demo key first, then user key)
            api_key = os.getenv("DEMO_ELEVEN_API_KEY") or os.getenv("ELEVEN_API_KEY")

            if not api_key:
                print("ℹ️ ElevenLabs: No API key found. Voice feedback disabled (text-only mode).")
                return

            # Try to initialize client
            from elevenlabs.client import ElevenLabs
            self.client = ElevenLabs(api_key=api_key)
            self.available = True

            key_type = "demo" if os.getenv("DEMO_ELEVEN_API_KEY") else "user"
            print(f"✅ ElevenLabs voice initialized ({key_type} key)")

        except ImportError:
            print("⚠️ ElevenLabs: Package not installed. Run: pip install elevenlabs")
        except Exception as e:
            print(f"⚠️ ElevenLabs: Initialization failed: {e}")

    def text_to_speech(self, text: str, emotion: str = "neutral") -> Optional[str]:
        """
        Convert text to speech and return path to temporary audio file.

        Args:
            text: Text to convert to speech
            emotion: Emotion hint (not used in current implementation)

        Returns:
            Path to temporary MP3 file, or None if voice unavailable
        """
        # Check if voice is enabled globally
        if os.getenv("VOICE_ENABLED", "true").lower() == "false":
            return None

        if not self.available or not self.client:
            return None

        try:
            # Generate audio using ElevenLabs API
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                output_format="mp3_44100_128"
            )

            # Convert generator/stream to bytes
            audio_bytes = b"".join(audio)

            # Save to temporary file (Gradio expects file path, not data URL)
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3",
                prefix="focusflow_voice_"
            )
            temp_file.write(audio_bytes)
            temp_file.close()

            return temp_file.name

        except Exception as e:
            # Graceful degradation - log error but don't crash
            print(f"⚠️ ElevenLabs: TTS failed: {e}")
            return None

    def get_focus_message_audio(self, verdict: str, message: str) -> Optional[str]:
        """
        Generate voice feedback for focus check results.

        Args:
            verdict: "On Track", "Distracted", or "Idle"
            message: Text message to speak

        Returns:
            Path to temporary audio file or None
        """
        if not self.available:
            return None

        # Add emotion/tone based on verdict (for future voice modulation)
        emotion_map = {
            "On Track": "cheerful",
            "Distracted": "concerned",
            "Idle": "motivating"
        }

        emotion = emotion_map.get(verdict, "neutral")
        return self.text_to_speech(message, emotion=emotion)

    def get_pomodoro_audio(self, event_type: str) -> Optional[str]:
        """
        Generate voice alerts for Pomodoro timer events.

        Args:
            event_type: "work_complete" or "break_complete"

        Returns:
            Path to temporary audio file or None
        """
        if not self.available:
            return None

        messages = {
            "work_complete": "Great work! Time for a 5-minute break. You've earned it!",
            "break_complete": "Break's over! Let's get back to work and stay focused!"
        }

        message = messages.get(event_type, "Timer complete!")
        return self.text_to_speech(message, emotion="cheerful")

    def test_voice(self) -> Dict[str, any]:
        """
        Test voice generation (for setup/debugging).

        Returns:
            Dict with status, message, and optional audio data
        """
        if not self.available:
            return {
                "status": "unavailable",
                "message": "Voice not available (no API key or initialization failed)",
                "audio": None
            }

        try:
            test_message = "Hello! FocusFlow voice is working perfectly!"
            audio = self.text_to_speech(test_message)

            if audio:
                return {
                    "status": "success",
                    "message": "Voice test successful!",
                    "audio": audio
                }
            else:
                return {
                    "status": "error",
                    "message": "Voice generation failed",
                    "audio": None
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Voice test failed: {str(e)}",
                "audio": None
            }


# Global voice generator instance
voice_generator = VoiceGenerator()


def get_voice_status() -> str:
    """
    Get human-readable voice status for UI display.

    Returns:
        Status string like "✅ ElevenLabs Voice Enabled" or "ℹ️ Voice Disabled"
    """
    if voice_generator.available:
        return "✅ ElevenLabs Voice Enabled"
    else:
        return "ℹ️ Voice Disabled (text-only mode)"
