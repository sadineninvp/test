"""
Agent State Definition
Defines the state structure for the autonomous agent graph
"""

from typing import TypedDict, List, Dict, Any, Optional, Literal
from langgraph.graph.message import AnyMessage


class AgentState(TypedDict):
    """
    State structure for the autonomous agent graph
    """
    # Messages (conversation history)
    messages: List[AnyMessage]
    
    # Request classification
    intent: Optional[Literal["chat", "code", "web", "action", "complex"]]
    mode: Optional[Literal["simple", "planning", "execution"]]
    
    # Planning
    plan: Optional[Dict[str, Any]]  # Multi-step plan
    current_step: Optional[int]
    steps: List[Dict[str, Any]]  # Plan steps with status
    
    # Execution
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    
    # Project context
    project_context: Optional[Dict[str, Any]]
    modified_files: List[str]
    created_files: List[str]
    
    # Verification
    verification_results: Optional[Dict[str, Any]]
    errors: List[str]
    
    # Human-in-the-loop
    requires_approval: bool
    approval_status: Optional[Literal["pending", "approved", "rejected"]]
    approval_message: Optional[str]
    
    # Session
    session_id: str
    user_id: Optional[str]
    
    # Memory context (from LangMem)
    memory_context: Optional[str]
    
    # Legacy state (for compatibility with existing ConversationState)
    conversation_state: Optional[Dict[str, Any]]
    state_manager: Optional[Dict[str, Any]]


def from_conversation_state(conversation_state, state_manager, session_id: str) -> AgentState:
    """
    Convert existing ConversationState and StateManager to AgentState
    
    Args:
        conversation_state: ConversationState instance
        state_manager: StateManager instance
        session_id: Session ID
        
    Returns:
        Initial AgentState
    """
    return AgentState(
        messages=[],
        intent=None,
        mode=None,
        plan=None,
        current_step=None,
        steps=[],
        tool_calls=[],
        tool_results=[],
        project_context=None,
        modified_files=[],
        created_files=[],
        verification_results=None,
        errors=[],
        requires_approval=False,
        approval_status=None,
        approval_message=None,
        session_id=session_id,
        user_id=None,
        memory_context=None,
        conversation_state={
            "last_file_shown": conversation_state.last_file_shown,
            "last_directory": conversation_state.last_directory,
            "recent_commands": conversation_state.recent_commands,
        } if conversation_state else None,
        state_manager={
            "current_directory": state_manager.current_directory,
            "session_id": state_manager.session_id,
        } if state_manager else None,
    )

