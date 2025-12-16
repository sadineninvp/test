"""
Edge functions for graph routing
"""

from typing import Literal
from .state import AgentState


def route_by_intent(state: AgentState) -> Literal["chat_agent", "planner", "agent"]:
    """
    Route based on intent classification
    
    Args:
        state: AgentState
        
    Returns:
        Next node name
    """
    intent = state.get("intent", "chat")
    mode = state.get("mode", "simple")
    
    if intent == "chat":
        return "chat_agent"
    elif mode == "planning":
        return "planner"
    else:
        return "agent"


def route_to_tools(state: AgentState) -> Literal["code_tools", "web_tools", "action_tools", "verify", "done"]:
    """
    Route to appropriate tool node based on tool calls
    
    Args:
        state: AgentState
        
    Returns:
        Next node name
    """
    tool_calls = state.get("tool_calls", [])
    
    if not tool_calls:
        # Check if plan is complete
        if state.get("plan"):
            plan = state["plan"]
            steps = plan.get("steps", [])
            current_step = state.get("current_step", 0)
            if current_step >= len(steps):
                return "verify"
        
        # No more tool calls, go to verify
        return "verify"
    
    # Route to appropriate tool node based on tool type
    code_tools = ["read_file", "write_file", "list_files"]
    web_tools = ["web_search", "fetch_url"]
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("name", "")
        if tool_name in code_tools:
            return "code_tools"
        elif tool_name in web_tools:
            return "web_tools"
        else:
            return "action_tools"
    
    return "action_tools"


def check_approval_needed(state: AgentState) -> Literal["hil", "summarize"]:
    """
    Check if approval is needed
    
    Args:
        state: AgentState
        
    Returns:
        Next node name
    """
    if state.get("requires_approval") and state.get("approval_status") == "pending":
        return "hil"
    else:
        return "summarize"


def check_approval_status(state: AgentState) -> Literal["summarize", "agent", "end"]:
    """
    Check approval status after HIL
    
    Args:
        state: AgentState
        
    Returns:
        Next node name
    """
    approval_status = state.get("approval_status")
    
    if approval_status == "approved":
        return "summarize"
    elif approval_status == "rejected":
        # Retry or end
        return "summarize"  # End with error message
    else:
        # Still pending
        return "end"  # Wait for approval

