"""
Command Center - Main orchestration class
Combines parser, router, orchestrator, and formatter
"""

from typing import Dict, Any

from .request_parser import RequestParser
from .action_router import ActionRouter
from .orchestrator import ActionOrchestrator
from .formatter import ResultFormatter


class CommandCenter:
    """
    Main Command Center class
    Orchestrates request parsing, routing, execution, and formatting
    """
    
    def __init__(self):
        """Initialize Command Center components"""
        self.parser = RequestParser()
        self.router = ActionRouter()
        self.orchestrator = ActionOrchestrator()
        self.formatter = ResultFormatter()
    
    def handle(self, request: str) -> Dict[str, Any]:
        """
        Handle a user request end-to-end
        
        Args:
            request: User's natural language request
            
        Returns:
            Dict with:
                - success: bool
                - message: str (formatted user message)
                - data: Dict (detailed execution data)
                - original_request: str
        """
        # Parse request
        parsed_intent = self.parser.parse(request)
        
        if parsed_intent["action"] == "unknown":
            return {
                "success": False,
                "message": self.formatter.format_unknown_action(request),
                "data": {"parsed_intent": parsed_intent},
                "original_request": request
            }
        
        # Route to action plan
        plan = self.router.route(parsed_intent)
        
        if not plan:
            return {
                "success": False,
                "message": f"No action plan found for: {parsed_intent['action']}",
                "data": {"parsed_intent": parsed_intent},
                "original_request": request
            }
        
        # Execute plan
        execution_result = self.orchestrator.execute_plan(plan, fail_fast=True)
        
        # Format result
        formatted_message = self.formatter.format(execution_result)
        
        return {
            "success": execution_result["success"],
            "message": formatted_message,
            "data": {
                "parsed_intent": parsed_intent,
                "plan": plan,
                "execution": execution_result
            },
            "original_request": request
        }
    
    def get_supported_actions(self) -> list:
        """Get list of supported action types"""
        return self.router.get_supported_actions()

