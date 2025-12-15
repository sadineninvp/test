"""
Conversation State Manager - Tracks conversation context across requests
"""

from typing import Optional, List, Dict, Any
from datetime import datetime


class ConversationState:
    """
    Manages conversation context and state
    Tracks files shown, directories, recent actions, etc.
    """
    
    def __init__(self, session_id: str = "default"):
        """
        Initialize conversation state
        
        Args:
            session_id: Unique identifier for this conversation session
        """
        self.session_id = session_id
        self.last_file_shown: Optional[str] = None
        self.last_file_content: Optional[str] = None
        self.last_file_structure: Optional[Dict[str, Any]] = None
        self.last_directory: Optional[str] = None
        self.recent_commands: List[str] = []
        self.file_history: List[str] = []
        self.recent_actions: List[Dict[str, Any]] = []
        self.max_history = 10  # Keep last 10 items
    
    def update_file_shown(self, file_path: str, content: str, structure: Optional[Dict[str, Any]] = None):
        """
        Update state when a file is shown to user
        
        Args:
            file_path: Path to the file
            content: File content (store snippet)
            structure: Code structure analysis (if available)
        """
        self.last_file_shown = file_path
        # Store first 2000 chars of content for context
        self.last_file_content = content[:2000] if content else None
        self.last_file_structure = structure
        
        if file_path not in self.file_history:
            self.file_history.append(file_path)
            # Keep only recent files
            if len(self.file_history) > self.max_history:
                self.file_history.pop(0)
        
        self._add_action("file_shown", {"file_path": file_path})
    
    def update_directory(self, directory: str):
        """
        Update current directory
        
        Args:
            directory: Current directory path
        """
        self.last_directory = directory
        self._add_action("directory_changed", {"directory": directory})
    
    def add_command(self, command: str):
        """
        Add a command to recent commands history
        
        Args:
            command: Command that was executed
        """
        self.recent_commands.append(command)
        if len(self.recent_commands) > self.max_history:
            self.recent_commands.pop(0)
    
    def _add_action(self, action_type: str, data: Dict[str, Any]):
        """Add an action to recent actions"""
        self.recent_actions.append({
            "type": action_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
        if len(self.recent_actions) > self.max_history:
            self.recent_actions.pop(0)
    
    def get_context_for_llm(self) -> str:
        """
        Generate context string to inject into LLM prompts
        
        Returns:
            Context string with relevant information
        """
        context_parts = []
        
        if self.last_file_shown:
            context_parts.append(f"Last file shown: {self.last_file_shown}")
            if self.last_file_structure:
                # Add structure info
                if self.last_file_structure.get("is_test_file"):
                    test_funcs = self.last_file_structure.get("test_functions", [])
                    if test_funcs:
                        func_names = [f["name"] for f in test_funcs]
                        context_parts.append(f"File structure: Contains test functions: {', '.join(func_names)}")
        
        if self.last_directory:
            context_parts.append(f"Current directory: {self.last_directory}")
        
        if self.recent_commands:
            last_cmd = self.recent_commands[-1]
            context_parts.append(f"Last command: {last_cmd}")
        
        if context_parts:
            return "Context:\n" + "\n".join(f"- {part}" for part in context_parts)
        
        return ""
    
    def clear(self):
        """Clear all conversation state"""
        self.last_file_shown = None
        self.last_file_content = None
        self.last_file_structure = None
        self.last_directory = None
        self.recent_commands = []
        self.file_history = []
        self.recent_actions = []


