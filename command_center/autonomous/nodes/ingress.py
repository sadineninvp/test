"""
Ingress Node - Policy Guard
First node that validates requests and initializes state
"""

from typing import Dict, Any
from ..graph.state import AgentState


def ingress_node(state: AgentState) -> AgentState:
    """
    Ingress node - Policy guard and state initialization
    
    Validates:
    - Request is not empty
    - Rate limiting (if implemented)
    - Permission checks (if implemented)
    - Safe mode validation
    
    Args:
        state: AgentState
        
    Returns:
        Updated AgentState
    """
    # Validate messages exist
    if not state.get("messages") or len(state.get("messages", [])) == 0:
        state["errors"] = state.get("errors", []) + ["No messages in request"]
        return state
    
    # Get user message
    user_message = None
    for msg in state.get("messages", []):
        if isinstance(msg, dict) and msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
        elif hasattr(msg, "content"):
            user_message = msg.content
            break
    
    if not user_message or not user_message.strip():
        state["errors"] = state.get("errors", []) + ["Empty request"]
        return state
    
    # Initialize state fields if not present
    if "errors" not in state:
        state["errors"] = []
    
    if "modified_files" not in state:
        state["modified_files"] = []
    
    if "created_files" not in state:
        state["created_files"] = []
    
    if "tool_calls" not in state:
        state["tool_calls"] = []
    
    if "tool_results" not in state:
        state["tool_results"] = []
    
    if "steps" not in state:
        state["steps"] = []
    
    if "requires_approval" not in state:
        state["requires_approval"] = False
    
    # Policy checks (can be expanded)
    # For now, just validate request is not empty
    
    return state

