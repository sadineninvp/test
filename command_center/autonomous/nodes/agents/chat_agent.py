"""
Chat Agent Node - Simple conversational agent for chat queries
"""

from typing import Dict, Any
from ...graph.state import AgentState
from ...utils.llm_client import get_llm_client
from langchain_core.messages import HumanMessage


def chat_agent_node(state: AgentState) -> AgentState:
    """
    Chat agent node - Simple conversational responses
    
    Args:
        state: AgentState
        
    Returns:
        Updated AgentState with chat response
    """
    # Get user message
    user_message = ""
    for msg in state.get("messages", []):
        if isinstance(msg, dict) and msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
        elif hasattr(msg, "content"):
            user_message = msg.content
            break
    
    if not user_message:
        return state
    
    try:
        llm = get_llm_client(temperature=0.7)
        
        # Simple chat response
        response = llm.invoke([HumanMessage(content=user_message)])
        
        # Add response to messages
        assistant_msg = {
            "role": "assistant",
            "content": response.content if hasattr(response, "content") else str(response)
        }
        state["messages"] = state.get("messages", []) + [assistant_msg]
        
    except Exception as e:
        state["errors"] = state.get("errors", []) + [f"Chat agent error: {str(e)}"]
    
    return state

