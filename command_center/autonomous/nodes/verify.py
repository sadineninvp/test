"""
Verify Node - Verifies execution results and checks for errors
"""

from typing import Dict, Any
from ..graph.state import AgentState
from action_agent import CommandExecutor
import os


def verify_node(state: AgentState) -> AgentState:
    """
    Verify node - Checks execution results and validates changes
    
    Args:
        state: AgentState
        
    Returns:
        Updated AgentState with verification results
    """
    verification_results = {
        "files_created": [],
        "files_modified": [],
        "files_exist": True,
        "errors": [],
        "warnings": []
    }
    
    # Check created files exist
    created_files = state.get("created_files", [])
    for file_path in created_files:
        if os.path.exists(file_path):
            verification_results["files_created"].append(file_path)
        else:
            verification_results["errors"].append(f"Created file does not exist: {file_path}")
            verification_results["files_exist"] = False
    
    # Check modified files exist
    modified_files = state.get("modified_files", [])
    for file_path in modified_files:
        if os.path.exists(file_path):
            verification_results["files_modified"].append(file_path)
        else:
            verification_results["warnings"].append(f"Modified file does not exist: {file_path}")
    
    # Check for errors in tool results
    tool_results = state.get("tool_results", [])
    for result in tool_results:
        if not result.get("success", True):
            error_msg = result.get("error", "Unknown error")
            verification_results["errors"].append(f"Tool error: {error_msg}")
    
    # Check if approval needed (dangerous operations)
    requires_approval = False
    approval_message = ""
    
    # Check for dangerous operations
    dangerous_patterns = [
        "rm -rf", "delete", "drop", "remove", "uninstall",
        "/etc/", "/usr/", "/var/", "system", "service"
    ]
    
    tool_calls = state.get("tool_calls", [])
    for tool_call in tool_calls:
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})
        
        # Check for file deletion
        if tool_name == "run_command":
            command = tool_args.get("command", "").lower()
            if any(pattern in command for pattern in dangerous_patterns):
                requires_approval = True
                approval_message = f"Dangerous command detected: {command}"
        
        # Check for system file modifications
        if tool_name == "write_file":
            file_path = tool_args.get("file_path", "")
            if any(pattern in file_path for pattern in ["/etc/", "/usr/", "/var/", "system"]):
                requires_approval = True
                approval_message = f"System file modification: {file_path}"
        
        # Check for service operations
        if tool_name in ["stop_service", "restart_service"]:
            service_name = tool_args.get("service_name", "")
            requires_approval = True
            approval_message = f"Service operation: {tool_name} on {service_name}"
    
    # Store verification results
    state["verification_results"] = verification_results
    state["requires_approval"] = requires_approval
    if requires_approval:
        state["approval_status"] = "pending"
        state["approval_message"] = approval_message
    
    return state

