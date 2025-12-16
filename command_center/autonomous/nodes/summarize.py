"""
Summarize Node - Creates final summary of execution
"""

from typing import Dict, Any
from ..graph.state import AgentState


def summarize_node(state: AgentState) -> AgentState:
    """
    Summarize node - Creates summary of what was done
    
    Args:
        state: AgentState
        
    Returns:
        Updated AgentState with summary
    """
    summary_parts = []
    
    # Files created
    created_files = state.get("created_files", [])
    if created_files:
        summary_parts.append(f"Created {len(created_files)} file(s):")
        for file_path in created_files:
            summary_parts.append(f"  - {file_path}")
    
    # Files modified
    modified_files = state.get("modified_files", [])
    if modified_files:
        summary_parts.append(f"\nModified {len(modified_files)} file(s):")
        for file_path in modified_files:
            summary_parts.append(f"  - {file_path}")
    
    # Tool results summary
    tool_results = state.get("tool_results", [])
    successful_tools = sum(1 for r in tool_results if r.get("success", True))
    total_tools = len(tool_results)
    
    if total_tools > 0:
        summary_parts.append(f"\nExecuted {successful_tools}/{total_tools} tool(s) successfully")
    
    # Errors
    errors = state.get("errors", [])
    if errors:
        summary_parts.append(f"\nErrors encountered:")
        for error in errors[:5]:  # Limit to first 5 errors
            summary_parts.append(f"  - {error}")
    
    # Verification results
    verification = state.get("verification_results", {})
    if verification:
        if verification.get("files_exist"):
            summary_parts.append("\n✅ All files verified successfully")
        if verification.get("errors"):
            summary_parts.append(f"\n⚠️ Verification errors: {len(verification['errors'])}")
    
    # Plan completion
    if state.get("plan"):
        plan = state["plan"]
        steps = plan.get("steps", [])
        completed_steps = sum(1 for s in steps if s.get("status") == "completed")
        total_steps = len(steps)
        summary_parts.append(f"\nPlan progress: {completed_steps}/{total_steps} steps completed")
    
    # Create summary
    summary = "\n".join(summary_parts) if summary_parts else "Task completed"
    
    # Add summary to state (can be used by API)
    state["summary"] = summary
    
    # Add summary as final message
    summary_message = {
        "role": "assistant",
        "content": summary
    }
    state["messages"] = state.get("messages", []) + [summary_message]
    
    return state

