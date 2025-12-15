"""
State Manager - Tracks working directory and other session state
"""

import os
import threading
from typing import Optional, List, Dict, Any


class StateManager:
    """
    Manages session state including current working directory
    Thread-safe for concurrent access
    """
    
    def __init__(self, session_id: str = "default", initial_directory: Optional[str] = None):
        """
        Initialize state manager
        
        Args:
            session_id: Unique identifier for this session
            initial_directory: Starting directory (defaults to current working directory)
        """
        self.session_id = session_id
        self._lock = threading.Lock()
        self.current_directory = os.path.abspath(initial_directory or os.getcwd())
        self.history: List[Dict[str, Any]] = []
        
        # Record initial directory
        self.history.append({
            "action": "initialize",
            "directory": self.current_directory,
            "timestamp": self._get_timestamp()
        })
    
    def change_directory(self, path: str) -> Dict[str, Any]:
        """
        Change the current working directory
        
        Args:
            path: Path to change to (absolute or relative to current directory)
            
        Returns:
            Dict with success status and details
        """
        with self._lock:
            try:
                # Resolve path (absolute or relative)
                if os.path.isabs(path):
                    target_path = os.path.abspath(path)
                else:
                    target_path = os.path.abspath(os.path.join(self.current_directory, path))
                
                # Validate path exists
                if not os.path.exists(target_path):
                    return {
                        "success": False,
                        "error": f"Path does not exist: {target_path}",
                        "directory": self.current_directory
                    }
                
                # Validate it's a directory
                if not os.path.isdir(target_path):
                    return {
                        "success": False,
                        "error": f"Path is not a directory: {target_path}",
                        "directory": self.current_directory
                    }
                
                # Change directory
                previous_directory = self.current_directory
                self.current_directory = target_path
                
                # Record in history
                self.history.append({
                    "action": "change_directory",
                    "from": previous_directory,
                    "to": target_path,
                    "timestamp": self._get_timestamp()
                })
                
                return {
                    "success": True,
                    "directory": self.current_directory,
                    "previous_directory": previous_directory
                }
                
            except PermissionError:
                return {
                    "success": False,
                    "error": f"Permission denied: {path}",
                    "directory": self.current_directory
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error changing directory: {str(e)}",
                    "directory": self.current_directory
                }
    
    def get_current_directory(self) -> str:
        """
        Get the current working directory
        
        Returns:
            Current directory path
        """
        with self._lock:
            return self.current_directory
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get directory change history
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of history entries
        """
        with self._lock:
            return self.history[-limit:]
    
    def reset(self) -> Dict[str, Any]:
        """
        Reset to the initial directory
        
        Returns:
            Dict with reset status
        """
        with self._lock:
            if self.history:
                initial_dir = self.history[0]["directory"]
                result = self.change_directory(initial_dir)
                return {
                    "success": result["success"],
                    "directory": result.get("directory", self.current_directory),
                    "message": f"Reset to initial directory: {initial_dir}"
                }
            return {
                "success": False,
                "error": "No history available",
                "directory": self.current_directory
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

