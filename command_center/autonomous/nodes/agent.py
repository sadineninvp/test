"""
Agent Node - ReAct Loop
Main agent node that executes tool-calling loop
"""

from typing import Dict, Any, List
from ..graph.state import AgentState
from ..utils.llm_client import get_llm_client
from ..tools.tool_registry import get_tools
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json


def agent_node(state: AgentState) -> AgentState:
    """
    Agent node - ReAct loop for tool calling
    
    Args:
        state: AgentState
        
    Returns:
        Updated AgentState with tool calls and results
    """
    # Get messages
    messages = state.get("messages", [])
    if not messages:
        return state
    
    # Get context from state
    context_parts = []
    if state.get("conversation_state", {}).get("last_file_shown"):
        context_parts.append(f"Last file shown: {state['conversation_state']['last_file_shown']}")
    if state.get("state_manager", {}).get("current_directory"):
        context_parts.append(f"Current directory: {state['state_manager']['current_directory']}")
    if state.get("memory_context"):
        context_parts.append(f"Context: {state['memory_context']}")
    
    context = "\n".join(context_parts) if context_parts else ""
    
    # Get plan if exists
    plan_info = ""
    if state.get("plan") and state.get("current_step") is not None:
        plan = state["plan"]
        current_step = state.get("current_step", 0)
        steps = plan.get("steps", [])
        if current_step < len(steps):
            plan_info = f"\n\nCurrent plan step {current_step + 1}/{len(steps)}: {steps[current_step].get('action', '')}"
    
    try:
        llm = get_llm_client()
        tools = get_tools()
        
        # System prompt
        system_prompt = """You are a helpful coding assistant that can execute system commands, manage services, and work with files on a computer.

You have access to tools that allow you to:
- Run shell commands
- Check, start, stop, and restart system services
- Get system information
- Read files (with code structure analysis for code files)
- Write files
- List directory contents
- Search the web
- Navigate directories

FILE OPERATIONS & CODE UNDERSTANDING:
- When reading code files, you receive structure analysis (functions, classes, imports, patterns)
- For test files, you can see all test functions
- When users reference "it" or "that file", they mean the last file you showed them
- Remember files you've read in this conversation
- When asked to edit code, suggest specific code that follows existing patterns

CONTEXT AWARENESS:
- Pay attention to context provided
- Use context to understand ambiguous requests

When a user makes a request:
1. Understand what they want to accomplish
2. Use context to resolve references
3. Use the available tools to perform the actions
4. For code edits, reference the structure you've seen and follow existing patterns
5. Provide clear, helpful responses based on the tool results

Always be helpful and explain what you're doing. If a tool call fails, explain why and suggest alternatives."""
        
        if plan_info:
            system_prompt += plan_info
        
        # Prepare messages for LLM
        llm_messages = []
        if context:
            llm_messages.append({"role": "system", "content": system_prompt + "\n\n" + context})
        else:
            llm_messages.append({"role": "system", "content": system_prompt})
        
        # Convert messages to LangChain format
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    llm_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    llm_messages.append(AIMessage(content=content))
                elif role == "tool":
                    llm_messages.append(ToolMessage(content=content, tool_call_id=msg.get("tool_call_id", "")))
        
        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(tools)
        
        # Get response
        response = llm_with_tools.invoke(llm_messages)
        
        # Extract tool calls
        tool_calls = []
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_calls.append({
                    "id": tool_call.get("id", ""),
                    "name": tool_call.get("name", ""),
                    "args": tool_call.get("args", {})
                })
        
        # Store tool calls in state
        state["tool_calls"] = tool_calls
        
        # Add assistant message to state
        assistant_msg = {
            "role": "assistant",
            "content": response.content if hasattr(response, "content") else "",
            "tool_calls": tool_calls
        }
        state["messages"] = messages + [assistant_msg]
        
        # If no tool calls, agent is done
        if not tool_calls:
            # Update plan step if exists
            if state.get("plan") and state.get("current_step") is not None:
                current_step = state.get("current_step", 0)
                steps = state["plan"].get("steps", [])
                if current_step < len(steps):
                    steps[current_step]["status"] = "completed"
                    state["current_step"] = current_step + 1
        
    except Exception as e:
        state["errors"] = state.get("errors", []) + [f"Agent error: {str(e)}"]
    
    return state

