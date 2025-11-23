"""
File monitoring using watchdog with content-aware diff detection.
"""
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from datetime import datetime
import threading


class ContentAwareHandler(FileSystemEventHandler):
    """Handler that tracks file changes with content awareness."""
    
    IGNORED_PATTERNS = [
        '.git', '__pycache__', '.env', 'node_modules', 
        '.venv', 'venv', '.idea', '.vscode',
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib'
    ]
    
    TEXT_EXTENSIONS = [
        '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', 
        '.json', '.md', '.txt', '.yaml', '.yml', '.toml',
        '.c', '.cpp', '.h', '.java', '.go', '.rs', '.rb'
    ]
    
    def __init__(self, callback: Optional[Callable] = None):
        """Initialize the handler with optional callback."""
        super().__init__()
        self.events: List[Dict] = []
        self.callback = callback
        self.last_event_time = {}
        self.debounce_seconds = 1.0
    
    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored."""
        path_parts = Path(path).parts
        for pattern in self.IGNORED_PATTERNS:
            if pattern in path_parts or path.endswith(pattern):
                return True
        return False
    
    def _is_text_file(self, path: str) -> bool:
        """Check if file is a text file we should read."""
        return any(path.endswith(ext) for ext in self.TEXT_EXTENSIONS)
    
    def _read_file_content(self, path: str, max_chars: int = 500) -> str:
        """Read last N characters of a text file."""
        try:
            if not os.path.exists(path) or not os.path.isfile(path):
                return ""
            
            if not self._is_text_file(path):
                return "[Binary file]"
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if len(content) > max_chars:
                    return f"...{content[-max_chars:]}"
                return content
        except Exception as e:
            return f"[Error reading file: {str(e)}]"
    
    def _debounce_event(self, path: str) -> bool:
        """Check if event should be debounced (too soon after last event)."""
        now = time.time()
        last_time = self.last_event_time.get(path, 0)
        
        if now - last_time < self.debounce_seconds:
            return True
        
        self.last_event_time[path] = now
        return False
    
    def _create_event(self, event_type: str, path: str):
        """Create and store an event."""
        if self._should_ignore(path):
            return
        
        if self._debounce_event(path):
            return
        
        event_data = {
            'type': event_type,
            'path': path,
            'filename': os.path.basename(path),
            'timestamp': datetime.now().isoformat(),
            'content': self._read_file_content(path) if event_type == 'modified' else ""
        }
        
        self.events.append(event_data)
        
        # Keep only last 50 events
        if len(self.events) > 50:
            self.events = self.events[-50:]
        
        if self.callback:
            self.callback(event_data)
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification."""
        if not event.is_directory:
            self._create_event('modified', str(event.src_path))
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation."""
        if not event.is_directory:
            self._create_event('created', str(event.src_path))
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion."""
        if not event.is_directory:
            self._create_event('deleted', str(event.src_path))
    
    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        """Get the most recent events."""
        return self.events[-limit:]
    
    def clear_events(self):
        """Clear all stored events."""
        self.events = []


class FileMonitor:
    """File monitor using watchdog."""
    
    def __init__(self):
        """Initialize the file monitor."""
        self.observer: Optional[Observer] = None
        self.handler: Optional[ContentAwareHandler] = None
        self.watching_path: Optional[str] = None
    
    def start(self, path: str, callback: Optional[Callable] = None):
        """Start monitoring a directory."""
        if self.observer and self.observer.is_alive():
            self.stop()
        
        if not os.path.exists(path):
            raise ValueError(f"Path does not exist: {path}")
        
        self.watching_path = path
        self.handler = ContentAwareHandler(callback)
        self.observer = Observer()
        self.observer.schedule(self.handler, path, recursive=True)
        self.observer.start()
    
    def stop(self):
        """Stop monitoring."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=2)
        self.observer = None
        self.handler = None
        self.watching_path = None
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent file activity."""
        if self.handler:
            return self.handler.get_recent_events(limit)
        return []
    
    def clear_activity(self):
        """Clear activity log."""
        if self.handler:
            self.handler.clear_events()
    
    def is_running(self) -> bool:
        """Check if monitor is running."""
        return self.observer is not None and self.observer.is_alive()
