"""
Result Formatter - Format execution results for users
"""

from typing import Dict, Any, List


class ResultFormatter:
    """
    Formats technical execution results into user-friendly messages
    """
    
    @staticmethod
    def format(result: Dict[str, Any]) -> str:
        """
        Format execution result into user-friendly message
        
        Args:
            result: Result from ActionOrchestrator.execute_plan()
            
        Returns:
            Formatted message string
        """
        if not result.get("success"):
            return ResultFormatter._format_error(result)
        
        steps = result.get("steps", [])
        final_result = result.get("final_result")
        
        if not steps:
            return "No actions were executed."
        
        # Format based on action type (infer from steps)
        if len(steps) == 1:
            return ResultFormatter._format_single_step(steps[0], final_result)
        else:
            return ResultFormatter._format_multi_step(steps, final_result)
    
    @staticmethod
    def _format_error(result: Dict[str, Any]) -> str:
        """Format error result"""
        errors = result.get("errors", [])
        if errors:
            error_msg = "; ".join(errors[:3])  # Limit to first 3 errors
            return f"✗ Error: {error_msg}"
        return "✗ Operation failed"
    
    @staticmethod
    def _format_single_step(step: Dict[str, Any], final_result: Any) -> str:
        """Format single step result"""
        function_name = step.get("function", "")
        result_data = step.get("result", {})
        
        if function_name == "check_service":
            service_name = result_data.get("service_name", "service")
            status = result_data.get("status", "unknown")
            is_running = result_data.get("is_running", False)
            
            status_icon = "✓" if is_running else "✗"
            return f"{status_icon} Service '{service_name}' status: {status}"
        
        elif function_name == "run_command":
            output = result_data.get("output", "")
            # Truncate long output
            if len(output) > 200:
                output = output[:200] + "..."
            return f"✓ Command executed successfully.\nOutput:\n{output}"
        
        elif function_name in ["start_service", "stop_service", "restart_service"]:
            service_name = result_data.get("service_name", "service")
            action = result_data.get("action", "action")
            return f"✓ Service '{service_name}' {action} completed successfully"
        
        else:
            # Generic formatting
            return f"✓ Operation completed successfully"
    
    @staticmethod
    def _format_multi_step(steps: List[Dict[str, Any]], final_result: Any) -> str:
        """Format multi-step result"""
        # Count successful steps
        successful_steps = sum(1 for step in steps if step.get("success", False))
        total_steps = len(steps)
        
        # Try to extract key information from final result
        if isinstance(final_result, dict):
            # Check if it's a service operation
            if "service_name" in final_result:
                service_name = final_result["service_name"]
                action = final_result.get("action", "operation")
                status_after = final_result.get("status_after") or final_result.get("status")
                
                if status_after:
                    return f"✓ Service '{service_name}' {action} completed. Final status: {status_after} ({successful_steps}/{total_steps} steps successful)"
                else:
                    return f"✓ Service '{service_name}' {action} completed ({successful_steps}/{total_steps} steps successful)"
        
        # Generic multi-step format
        return f"✓ Operation completed successfully ({successful_steps}/{total_steps} steps successful)"
    
    @staticmethod
    def format_unknown_action(original_request: str) -> str:
        """Format message for unknown actions"""
        return f"❓ I don't understand the request: '{original_request}'. Please try a different format."

