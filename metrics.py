"""
Productivity metrics tracking for FocusFlow.
Tracks focus scores, completion rates, and streaks.
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json


class MetricsTracker:
    """Tracks productivity metrics and focus history."""
    
    def __init__(self, db_path: str = "focusflow.db"):
        """Initialize metrics tracker with SQLite database."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create metrics tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Focus check history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS focus_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                task_title TEXT,
                verdict TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Daily streaks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                on_track_count INTEGER DEFAULT 0,
                distracted_count INTEGER DEFAULT 0,
                idle_count INTEGER DEFAULT 0,
                max_consecutive_on_track INTEGER DEFAULT 0,
                focus_score REAL DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_focus_check(self, task_id: int, task_title: str, verdict: str, message: str):
        """Log a focus check result."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO focus_history (task_id, task_title, verdict, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, task_title, verdict, message, datetime.now()))
        
        # Update today's streak data
        today = datetime.now().date()
        
        # Get or create today's streak record
        cursor.execute("SELECT * FROM streaks WHERE date = ?", (today,))
        row = cursor.fetchone()
        
        if row:
            # Update existing record
            on_track = row[2] + (1 if verdict == "On Track" else 0)
            distracted = row[3] + (1 if verdict == "Distracted" else 0)
            idle = row[4] + (1 if verdict == "Idle" else 0)
            
            # Calculate consecutive on-track streak
            cursor.execute("""
                SELECT verdict FROM focus_history 
                WHERE DATE(timestamp) = ? 
                ORDER BY timestamp DESC LIMIT 20
            """, (today,))
            recent_verdicts = [r[0] for r in cursor.fetchall()]
            recent_verdicts.reverse()
            
            consecutive = 0
            for v in reversed(recent_verdicts):
                if v == "On Track":
                    consecutive += 1
                else:
                    break
            
            max_consecutive = max(row[5], consecutive)
            
            # Calculate focus score (0-100)
            total_checks = on_track + distracted + idle
            focus_score = (on_track / total_checks * 100) if total_checks > 0 else 0
            
            cursor.execute("""
                UPDATE streaks 
                SET on_track_count = ?, distracted_count = ?, idle_count = ?, 
                    max_consecutive_on_track = ?, focus_score = ?
                WHERE date = ?
            """, (on_track, distracted, idle, max_consecutive, focus_score, today))
        else:
            # Create new record
            on_track = 1 if verdict == "On Track" else 0
            distracted = 1 if verdict == "Distracted" else 0
            idle = 1 if verdict == "Idle" else 0
            focus_score = (on_track / 1 * 100) if (on_track + distracted + idle) > 0 else 0
            
            cursor.execute("""
                INSERT INTO streaks (date, on_track_count, distracted_count, idle_count, 
                                    max_consecutive_on_track, focus_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (today, on_track, distracted, idle, on_track, focus_score))
        
        conn.commit()
        conn.close()
    
    def get_today_stats(self) -> Dict:
        """Get today's productivity statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute("SELECT * FROM streaks WHERE date = ?", (today,))
        row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            return {
                "on_track": 0,
                "distracted": 0,
                "idle": 0,
                "max_streak": 0,
                "focus_score": 0,
                "total_checks": 0
            }
        
        return {
            "on_track": row[2],
            "distracted": row[3],
            "idle": row[4],
            "max_streak": row[5],
            "focus_score": round(row[6], 1),
            "total_checks": row[2] + row[3] + row[4]
        }
    
    def get_weekly_stats(self) -> List[Dict]:
        """Get last 7 days of statistics."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        seven_days_ago = datetime.now().date() - timedelta(days=6)
        
        cursor.execute("""
            SELECT date, on_track_count, distracted_count, idle_count, focus_score
            FROM streaks
            WHERE date >= ?
            ORDER BY date DESC
        """, (seven_days_ago,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_focus_history(self, limit: int = 20) -> List[Dict]:
        """Get recent focus check history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT task_title, verdict, message, timestamp
            FROM focus_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_current_streak(self) -> int:
        """Get current consecutive 'On Track' streak."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        cursor.execute("""
            SELECT verdict FROM focus_history 
            WHERE DATE(timestamp) = ? 
            ORDER BY timestamp DESC LIMIT 50
        """, (today,))
        
        verdicts = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        streak = 0
        for verdict in verdicts:
            if verdict == "On Track":
                streak += 1
            else:
                break
        
        return streak
    
    def get_chart_data(self) -> Dict:
        """Get data formatted for charts."""
        weekly = self.get_weekly_stats()
        
        # Prepare data for charts
        dates = []
        focus_scores = []
        on_track_counts = []
        distracted_counts = []
        idle_counts = []
        
        # Fill in missing days with zeros
        for i in range(7):
            date = datetime.now().date() - timedelta(days=6-i)
            dates.append(date.strftime("%m/%d"))
            
            # Find matching data
            day_data = next((d for d in weekly if str(d['date']) == str(date)), None)
            
            if day_data:
                focus_scores.append(day_data['focus_score'])
                on_track_counts.append(day_data['on_track_count'])
                distracted_counts.append(day_data['distracted_count'])
                idle_counts.append(day_data['idle_count'])
            else:
                focus_scores.append(0)
                on_track_counts.append(0)
                distracted_counts.append(0)
                idle_counts.append(0)
        
        return {
            "dates": dates,
            "focus_scores": focus_scores,
            "on_track": on_track_counts,
            "distracted": distracted_counts,
            "idle": idle_counts
        }
