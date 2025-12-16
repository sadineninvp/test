"""
Action Tools Node - Executes action-related tools
"""

from typing import Dict, Any
from ...graph.state import AgentState
from ...tools.tool_registry import get_action_tools
from langchain_core.messages import ToolMessage


def action_tools_node(state: AgentState) -> AgentState:
    """
    Execute action-related tools
    
    Args:
        state: AgentState with tool_calls
        
    Returns:
        Updated AgentState with tool results
    """
    tool_calls = state.get("tool_calls", [])
    if not tool_calls:
        return state
    
    # Get action tools
    action_tools = {tool.name: tool for tool in get_action_tools()}
    
    # Execute action tools
    tool_results = []
    tool_messages = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})
        tool_id = tool_call.get("id", "")
        
        if tool_name in action_tools:
            try:
                # Execute tool
                result = action_tools[tool_name].invoke(tool_args)
                
                tool_results.append({
                    "tool_name": tool_name,
                    "success": result.get("success", True),
                    "result": result
                })
                
                # Create tool message
                result_str = str(result) if not isinstance(result, dict) else str(result)
                tool_messages.append(ToolMessage(
                    content=result_str,
                    tool_call_id=tool_id
                ))
                
            except Exception as e:
                tool_results.append({
                    "tool_name": tool_name,
                    "success": False,
                    "error": str(e)
                })
                tool_messages.append(ToolMessage(
                    content=f"Error: {str(e)}",
                    tool_call_id=tool_id
                ))
    
    # Update state
    state["tool_results"] = state.get("tool_results", []) + tool_results
    state["messages"] = state.get("messages", []) + tool_messages
    
    return state

