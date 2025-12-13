"""
Audit Logger for Action Agent
Logs all actions for security and debugging
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .config import LOG_DIR, LOG_FILE


class ActionLogger:
    """Logs all agent actions to file and database"""
    
    def __init__(self, log_file: Optional[Path] = None, use_db: bool = True):
        """
        Initialize logger
        
        Args:
            log_file: Path to log file (defaults to config)
            use_db: Whether to use SQLite database for logs
        """
        self.log_file = log_file or LOG_FILE
        self.use_db = use_db
        self.db_path = LOG_DIR / "action_agent.db"
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database if using it
        if self.use_db:
            self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for structured logging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action TEXT NOT NULL,
                result TEXT,
                success INTEGER NOT NULL,
                error_message TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def log(
        self,
        action_type: str,
        action: str,
        result: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an action
        
        Args:
            action_type: Type of action (e.g., 'command', 'service', 'monitor')
            action: The action performed (e.g., command string)
            result: Result/output of the action
            success: Whether action succeeded
            error_message: Error message if failed
            metadata: Additional metadata (dict)
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare log entry
        log_entry = {
            "timestamp": timestamp,
            "action_type": action_type,
            "action": action,
            "result": result,
            "success": success,
            "error_message": error_message,
            "metadata": metadata or {}
        }
        
        # Write to file
        self._write_to_file(log_entry)
        
        # Write to database if enabled
        if self.use_db:
            self._write_to_db(log_entry)
    
    def _write_to_file(self, entry: Dict[str, Any]):
        """Write log entry to text file"""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Warning: Failed to write to log file: {e}")
    
    def _write_to_db(self, entry: Dict[str, Any]):
        """Write log entry to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO action_logs 
                (timestamp, action_type, action, result, success, error_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry["timestamp"],
                entry["action_type"],
                entry["action"],
                entry["result"],
                1 if entry["success"] else 0,
                entry["error_message"],
                json.dumps(entry["metadata"])
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Failed to write to database: {e}")
    
    def get_recent_logs(self, limit: int = 50) -> list:
        """Get recent log entries from database"""
        if not self.use_db:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, action_type, action, success, error_message
                FROM action_logs
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "timestamp": row[0],
                    "action_type": row[1],
                    "action": row[2],
                    "success": bool(row[3]),
                    "error_message": row[4]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Warning: Failed to read logs: {e}")
            return []

