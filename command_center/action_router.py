"""
Action Router - Route parsed intents to action plans
Uses hardcoded mappings (no LLM)
"""

from typing import List, Dict, Any


class ActionRouter:
    """
    Routes parsed intents to action plans (sequences of steps)
    Uses hardcoded mappings
    """
    
    def __init__(self):
        """Initialize router with action plan mappings"""
        # Define action plans for each action type
        self.action_plans = {
            "restart_service": [
                {"step": "check", "function": "check_service", "args": ["target"]},
                {"step": "stop", "function": "stop_service", "args": ["target"]},
                {"step": "start", "function": "start_service", "args": ["target"]},
                {"step": "verify", "function": "check_service", "args": ["target"]}
            ],
            "start_service": [
                {"step": "check", "function": "check_service", "args": ["target"]},
                {"step": "start", "function": "start_service", "args": ["target"]},
                {"step": "verify", "function": "check_service", "args": ["target"]}
            ],
            "stop_service": [
                {"step": "check", "function": "check_service", "args": ["target"]},
                {"step": "stop", "function": "stop_service", "args": ["target"]},
                {"step": "verify", "function": "check_service", "args": ["target"]}
            ],
            "check_service": [
                {"step": "check", "function": "check_service", "args": ["target"]}
            ],
            "run_command": [
                {"step": "execute", "function": "run_command", "args": ["target"]}
            ],
            "list_services": [
                {"step": "list", "function": "list_services", "args": []}
            ]
        }
    
    def route(self, parsed_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Route a parsed intent to an action plan
        
        Args:
            parsed_intent: Parsed intent from RequestParser
            
        Returns:
            List of action steps to execute
        """
        action_type = parsed_intent.get("action")
        target = parsed_intent.get("target")
        
        if action_type == "unknown":
            return []  # No plan for unknown actions
        
        # Get the base plan
        base_plan = self.action_plans.get(action_type, [])
        
        # Replace placeholder "target" with actual target value
        plan = []
        for step in base_plan:
            step_copy = step.copy()
            # Replace args
            step_copy["args"] = [
                target if arg == "target" else arg
                for arg in step["args"]
            ]
            plan.append(step_copy)
        
        return plan
    
    def get_supported_actions(self) -> List[str]:
        """Get list of supported action types"""
        return list(self.action_plans.keys())

