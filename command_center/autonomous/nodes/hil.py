"""
Human-in-the-Loop Node - Handles approval requests
"""

from typing import Dict, Any
from ..graph.state import AgentState
from langgraph.graph import interrupt


def hil_node(state: AgentState) -> AgentState:
    """
    Human-in-the-Loop node - Pauses execution for approval
    
    Args:
        state: AgentState
        
    Returns:
        Updated AgentState (may pause execution)
    """
    # Check if approval is needed
    if not state.get("requires_approval"):
        return state
    
    approval_status = state.get("approval_status")
    
    if approval_status == "pending":
        # Pause execution and wait for user approval
        interrupt()  # LangGraph function that pauses graph
        return state
    
    elif approval_status == "approved":
        # Continue execution
        state["requires_approval"] = False
        return state
    
    elif approval_status == "rejected":
        # Cancel operation
        state["errors"] = state.get("errors", []) + ["Operation rejected by user"]
        state["requires_approval"] = False
        return state
    
    return state

