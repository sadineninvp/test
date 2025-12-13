"""
Request Parser - Parse user requests into structured intents
Uses simple pattern matching (hardcoded rules)
"""

import re
from typing import Dict, Any, Optional


class RequestParser:
    """
    Parses natural language requests into structured action intents
    Uses pattern matching (hardcoded rules)
    """
    
    def __init__(self):
        """Initialize request parser with pattern definitions"""
        # Define patterns for common requests
        self.patterns = [
            # Restart service patterns
            (r"restart\s+(\w+)", "restart_service"),
            (r"reboot\s+(\w+)", "restart_service"),
            (r"reload\s+(\w+)", "restart_service"),
            
            # Start service patterns
            (r"start\s+(\w+)", "start_service"),
            (r"start\s+the\s+(\w+)", "start_service"),
            
            # Stop service patterns
            (r"stop\s+(\w+)", "stop_service"),
            (r"stop\s+the\s+(\w+)", "stop_service"),
            
            # Check/Status patterns
            (r"check\s+(\w+)", "check_service"),
            (r"status\s+of\s+(\w+)", "check_service"),
            (r"status\s+(\w+)", "check_service"),
            (r"is\s+(\w+)\s+running", "check_service"),
            (r"(\w+)\s+status", "check_service"),
            
            # Run command patterns
            (r"run\s+command\s+(.+)", "run_command"),
            (r"execute\s+(.+)", "run_command"),
            (r"run\s+(.+)", "run_command"),
            
            # List/Show patterns
            (r"list\s+services", "list_services"),
            (r"show\s+services", "list_services"),
            (r"what\s+services\s+are\s+running", "list_services"),
        ]
    
    def parse(self, request: str) -> Dict[str, Any]:
        """
        Parse a user request into structured intent
        
        Args:
            request: User's natural language request
            
        Returns:
            Dict with keys:
                - action: str (action type)
                - target: str (target service/command)
                - original_request: str
                - confidence: float (0-1, always 1.0 for hardcoded)
        """
        request = request.strip().lower()
        
        # Try to match patterns
        for pattern, action_type in self.patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if action_type in ["restart_service", "start_service", "stop_service", "check_service"]:
                    return {
                        "action": action_type,
                        "target": groups[0],
                        "original_request": request,
                        "confidence": 1.0
                    }
                elif action_type == "run_command":
                    # Extract the command
                    command = match.group(1).strip()
                    return {
                        "action": action_type,
                        "target": command,
                        "original_request": request,
                        "confidence": 1.0
                    }
                elif action_type == "list_services":
                    return {
                        "action": action_type,
                        "target": None,
                        "original_request": request,
                        "confidence": 1.0
                    }
        
        # No pattern matched - return unknown
        return {
            "action": "unknown",
            "target": None,
            "original_request": request,
            "confidence": 0.0
        }

