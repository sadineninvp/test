"""
Result Formatter - Format API responses for display
"""

from typing import Dict, Any, Optional


class ResultFormatter:
    """Formats Command Center API responses for display"""
    
    @staticmethod
    def format(result: Dict[str, Any], output_format: str = "pretty") -> str:
        """
        Format API response
        
        Args:
            result: API response dict
            output_format: "pretty" or "json"
            
        Returns:
            Formatted string
        """
        if output_format == "json":
            return ResultFormatter._format_json(result)
        else:
            return ResultFormatter._format_pretty(result)
    
    @staticmethod
    def _format_pretty(result: Dict[str, Any]) -> str:
        """Format as pretty text"""
        lines = []
        
        # Check for errors first
        if "error" in result:
            error_type = result.get("error", "unknown")
            if error_type == "connection_error":
                lines.append("❌ Connection Error")
                lines.append("")
                lines.append(result.get("message", "Could not connect to server"))
                lines.append("")
                lines.append("Make sure the Command Center server is running:")
                lines.append("  uvicorn command_center.api:app --reload")
                return "\n".join(lines)
            elif error_type == "timeout":
                lines.append("⏱️  Timeout Error")
                lines.append("")
                lines.append(result.get("message", "Request timed out"))
                return "\n".join(lines)
        
        # Success/Error indicator
        success = result.get("success", False)
        status_icon = "✅" if success else "❌"
        
        # Message
        message = result.get("message", "No message")
        lines.append(f"{status_icon} {message}")
        
        # Mode indicator
        mode = result.get("mode", "unknown")
        if mode == "phase3":
            lines.append(f"   (LLM-powered)")
        elif mode == "phase2":
            lines.append(f"   (Hardcoded routing)")
        
        # Additional data (optional, verbose mode)
        data = result.get("data", {})
        if data and isinstance(data, dict):
            # Show execution details if available
            execution = data.get("execution", {})
            if execution:
                steps = execution.get("steps", [])
                if steps:
                    lines.append("")
                    lines.append("Steps executed:")
                    for i, step in enumerate(steps, 1):
                        step_name = step.get("step", f"step_{i}")
                        step_success = step.get("success", False)
                        step_icon = "✓" if step_success else "✗"
                        lines.append(f"  {step_icon} {step_name}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_json(result: Dict[str, Any]) -> str:
        """Format as JSON"""
        import json
        return json.dumps(result, indent=2, default=str)

