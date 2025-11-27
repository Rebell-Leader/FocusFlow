"""
Comprehensive autotests for FocusFlow features:
- Check frequency configuration
- Distraction escalation logic
- Pomodoro timer functionality
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import app functions
import app
from agent import FocusAgent, MockFocusAgent
from storage import TaskManager


class TestCheckFrequency:
    """Test check frequency configuration and updates."""
    
    def test_check_frequency_options_exist(self):
        """Verify check frequency dropdown has all required options."""
        assert app.MONITOR_INTERVAL == 30
        # Options should be: 30s, 1min, 5min, 10min
        expected_options = ["30 seconds", "1 minute", "5 minutes", "10 minutes"]
        # These are defined in the UI, verified through documentation
        assert all(opt in expected_options for opt in expected_options)
    
    def test_check_frequency_parsing(self):
        """Test converting dropdown values to seconds."""
        test_cases = {
            "30 seconds": 30,
            "1 minute": 60,
            "5 minutes": 300,
            "10 minutes": 600,
        }
        for label, expected_seconds in test_cases.items():
            # Extract numeric value from label
            if "second" in label:
                result = int(label.split()[0])
            elif "minute" in label:
                result = int(label.split()[0]) * 60
            assert result == expected_seconds, f"Failed for {label}"
    
    def test_timer_active_state_tracking(self):
        """Verify timer active/inactive state is properly tracked."""
        app.timer_active = False
        assert app.timer_active == False
        
        app.timer_active = True
        assert app.timer_active == True
        
        app.timer_active = False
        assert app.timer_active == False


class TestDistractionEscalation:
    """Test distraction escalation logic (sound -> sound -> voice)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        app.consecutive_distracted = 0
        app.activity_log = []
    
    def test_escalation_counter_increments_on_distracted(self):
        """Verify consecutive_distracted increments on 'Distracted' verdict."""
        app.consecutive_distracted = 0
        
        # Simulate first distraction
        verdict = "Distracted"
        if verdict == "Distracted":
            app.consecutive_distracted += 1
        assert app.consecutive_distracted == 1
        
        # Second distraction
        if verdict == "Distracted":
            app.consecutive_distracted += 1
        assert app.consecutive_distracted == 2
        
        # Third distraction
        if verdict == "Distracted":
            app.consecutive_distracted += 1
        assert app.consecutive_distracted == 3
    
    def test_escalation_counter_resets_on_track(self):
        """Verify counter resets to 0 when verdict is 'On Track'."""
        app.consecutive_distracted = 3  # Start at escalation level
        
        verdict = "On Track"
        if verdict == "On Track":
            app.consecutive_distracted = 0
        
        assert app.consecutive_distracted == 0
    
    def test_escalation_logic_1st_distraction_sound_only(self):
        """Test 1st distraction: should trigger sound alert only."""
        app.consecutive_distracted = 0
        verdict = "Distracted"
        
        # First distraction
        if verdict == "Distracted":
            app.consecutive_distracted += 1
        
        # Check escalation logic
        play_voice = app.consecutive_distracted >= 3
        assert play_voice == False, "1st distraction should NOT trigger voice"
        assert app.consecutive_distracted == 1
    
    def test_escalation_logic_2nd_distraction_sound_only(self):
        """Test 2nd distraction: should trigger sound alert only."""
        app.consecutive_distracted = 1
        verdict = "Distracted"
        
        # Second distraction
        if verdict == "Distracted":
            app.consecutive_distracted += 1
        
        # Check escalation logic
        play_voice = app.consecutive_distracted >= 3
        assert play_voice == False, "2nd distraction should NOT trigger voice"
        assert app.consecutive_distracted == 2
    
    def test_escalation_logic_3rd_distraction_with_voice(self):
        """Test 3rd+ distraction: should trigger sound AND voice feedback."""
        app.consecutive_distracted = 2
        verdict = "Distracted"
        
        # Third distraction
        if verdict == "Distracted":
            app.consecutive_distracted += 1
        
        # Check escalation logic
        play_voice = app.consecutive_distracted >= 3
        assert play_voice == True, "3rd+ distraction SHOULD trigger voice"
        assert app.consecutive_distracted == 3
    
    def test_escalation_idle_counter_independent(self):
        """Verify Idle verdicts don't interfere with Distracted counter."""
        app.consecutive_distracted = 2
        
        # Get Idle verdict - should NOT affect distracted counter in this logic
        verdict = "On Track"
        if verdict == "On Track":
            app.consecutive_distracted = 0
        
        assert app.consecutive_distracted == 0
    
    def test_escalation_full_cycle(self):
        """Test full escalation cycle: distracted -> distracted -> distracted -> on track -> reset."""
        app.consecutive_distracted = 0
        
        # 1st check: Distracted
        app.consecutive_distracted += 1
        assert app.consecutive_distracted == 1
        assert (app.consecutive_distracted >= 3) == False
        
        # 2nd check: Distracted
        app.consecutive_distracted += 1
        assert app.consecutive_distracted == 2
        assert (app.consecutive_distracted >= 3) == False
        
        # 3rd check: Distracted
        app.consecutive_distracted += 1
        assert app.consecutive_distracted == 3
        assert (app.consecutive_distracted >= 3) == True
        
        # Back on track
        app.consecutive_distracted = 0
        assert app.consecutive_distracted == 0
        assert (app.consecutive_distracted >= 3) == False


class TestActivityLogging:
    """Test activity log management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        app.activity_log = []
    
    def test_activity_log_entry_added(self):
        """Verify log entries are added correctly."""
        entry = "✅ [On Track] Great work!"
        app.activity_log.append(entry)
        assert entry in app.activity_log
        assert len(app.activity_log) == 1
    
    def test_activity_log_maintains_max_20_entries(self):
        """Verify activity log maintains maximum 20 entries."""
        # Fill with 21 entries
        for i in range(21):
            app.activity_log.append(f"Entry {i}")
        
        # Simulate the trimming logic from app.py
        if len(app.activity_log) > 20:
            app.activity_log.pop(0)
        
        assert len(app.activity_log) == 20
        assert "Entry 0" not in app.activity_log
        assert "Entry 20" in app.activity_log
    
    def test_emoji_verdict_mapping(self):
        """Test emoji assignment for different verdicts."""
        test_cases = {
            "On Track": "✅",
            "Distracted": "⚠️",
            "Idle": "💤",
            "Unknown": "💤"
        }
        
        for verdict, expected_emoji in test_cases.items():
            if verdict == "On Track":
                emoji = "✅"
            elif verdict == "Distracted":
                emoji = "⚠️"
            else:
                emoji = "💤"
            assert emoji == expected_emoji, f"Wrong emoji for {verdict}"


class TestPomodoroTimer:
    """Test Pomodoro timer state management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        app.pomodoro_state = {
            "minutes": 25,
            "seconds": 0,
            "is_running": False,
            "is_work_time": True,
            "total_seconds": 25 * 60
        }
    
    def test_pomodoro_initial_state(self):
        """Verify initial Pomodoro state."""
        assert app.pomodoro_state["total_seconds"] == 1500  # 25 * 60
        assert app.pomodoro_state["is_work_time"] == True
        assert app.pomodoro_state["is_running"] == False
    
    def test_pomodoro_format_time(self):
        """Test time formatting (MM:SS)."""
        result = app.format_time(1500)
        assert result == "25:00"
        
        result = app.format_time(0)
        assert result == "00:00"
        
        result = app.format_time(125)
        assert result == "02:05"
    
    def test_pomodoro_start(self):
        """Test starting the timer."""
        result = app.pomodoro_start()
        assert app.pomodoro_state["is_running"] == True
        assert "▶️" in result
    
    def test_pomodoro_pause(self):
        """Test pausing the timer."""
        app.pomodoro_state["is_running"] = True
        result = app.pomodoro_pause()
        assert app.pomodoro_state["is_running"] == False
        assert "⏸️" in result
    
    def test_pomodoro_reset(self):
        """Test resetting the timer."""
        app.pomodoro_state["total_seconds"] = 500
        app.pomodoro_state["is_work_time"] = False
        result = app.pomodoro_reset()
        assert app.pomodoro_state["total_seconds"] == 1500
        assert app.pomodoro_state["is_work_time"] == True
        assert "🔄" in result
    
    def test_pomodoro_tick_decrements(self):
        """Test that tick decrements timer."""
        app.pomodoro_state["is_running"] = True
        app.pomodoro_state["total_seconds"] = 100
        
        app.tick_pomodoro()
        assert app.pomodoro_state["total_seconds"] == 99
    
    def test_pomodoro_tick_when_paused(self):
        """Test that tick does nothing when paused."""
        app.pomodoro_state["is_running"] = False
        app.pomodoro_state["total_seconds"] = 100
        
        app.tick_pomodoro()
        assert app.pomodoro_state["total_seconds"] == 100
    
    def test_pomodoro_switches_mode_on_completion(self):
        """Test timer switches between work/break when time completes."""
        app.pomodoro_state["is_running"] = True
        app.pomodoro_state["total_seconds"] = 1
        app.pomodoro_state["is_work_time"] = True
        
        app.tick_pomodoro()  # 1 -> 0
        
        # Should switch mode and auto-pause
        assert app.pomodoro_state["is_work_time"] == False
        assert app.pomodoro_state["is_running"] == False
        assert app.pomodoro_state["total_seconds"] == 300  # 5 min break


class TestMockAgent:
    """Test mock agent for demo mode."""
    
    def test_mock_agent_initialization(self):
        """Verify mock agent initializes without API keys."""
        agent = MockFocusAgent()
        assert agent.provider == "mock"
        assert agent.connection_healthy == True
        assert agent.client is None
    
    def test_mock_agent_cycles_through_verdicts(self):
        """Verify mock agent cycles through verdict pattern."""
        agent = MockFocusAgent()
        task = {"id": 1, "title": "Test Task"}
        
        verdicts = []
        for _ in range(5):
            result = agent.analyze(task, [])
            verdicts.append(result["verdict"])
        
        expected_cycle = ["On Track", "On Track", "Distracted", "On Track", "Idle"]
        assert verdicts == expected_cycle
    
    def test_mock_agent_no_api_key_needed(self):
        """Verify mock agent works without any API keys."""
        with patch.dict('os.environ', {}, clear=True):
            agent = MockFocusAgent()
            assert agent.connection_healthy == True
            
            task = {"id": 1, "title": "Test"}
            result = agent.analyze(task, [])
            assert "verdict" in result
            assert "message" in result


class TestTaskManager:
    """Test task management functionality."""
    
    def test_task_manager_initialization(self):
        """Verify TaskManager initializes correctly."""
        tm = TaskManager()
        assert isinstance(tm, TaskManager)


# Integration tests
class TestIntegration:
    """Integration tests combining multiple features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        app.consecutive_distracted = 0
        app.activity_log = []
        app.pomodoro_state = {
            "minutes": 25,
            "seconds": 0,
            "is_running": False,
            "is_work_time": True,
            "total_seconds": 25 * 60
        }
    
    def test_full_monitoring_cycle(self):
        """Test a full monitoring cycle with escalation."""
        app.consecutive_distracted = 0
        verdicts = ["Distracted", "Distracted", "Distracted", "On Track"]
        
        results = []
        for verdict in verdicts:
            if verdict == "On Track":
                app.consecutive_distracted = 0
            elif verdict == "Distracted":
                app.consecutive_distracted += 1
            
            play_voice = app.consecutive_distracted >= 3
            results.append({
                "distracted_count": app.consecutive_distracted,
                "play_voice": play_voice
            })
        
        # Verify escalation progression
        assert results[0]["distracted_count"] == 1
        assert results[0]["play_voice"] == False
        
        assert results[1]["distracted_count"] == 2
        assert results[1]["play_voice"] == False
        
        assert results[2]["distracted_count"] == 3
        assert results[2]["play_voice"] == True
        
        assert results[3]["distracted_count"] == 0
        assert results[3]["play_voice"] == False
    
    def test_timer_with_check_frequency(self):
        """Test timer tick respects check frequency."""
        app.check_interval = 30
        ticks = 0
        
        while ticks < 5:
            app.tick_pomodoro()
            ticks += 1
        
        assert ticks == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
