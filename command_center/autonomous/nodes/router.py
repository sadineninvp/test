"""
Router Node - Intent Classifier
Classifies requests and routes to appropriate agent
"""

from typing import Dict, Any, Literal
from ..graph.state import AgentState
from ..utils.llm_client import get_llm_client


def router_node(state: AgentState) -> AgentState:
    """
    Router node - Classifies request intent and sets routing mode
    
    Classifies into:
    - "chat": Simple conversational queries
    - "code": Code-related tasks
    - "web": Web search/research tasks
    - "action": System action tasks
    - "complex": Multi-step complex tasks
    
    Args:
        state: AgentState
        
    Returns:
        Updated AgentState with intent and mode set
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
        state["intent"] = "chat"
        state["mode"] = "simple"
        return state
    
    # Simple keyword-based routing (can be enhanced with LLM)
    user_lower = user_message.lower()
    
    # Check for code-related keywords
    code_keywords = [
        "file", "code", "function", "class", "import", "refactor",
        "edit", "create", "modify", "add", "remove", "test", "bug",
        "fix", "implement", "feature", "module", "package"
    ]
    
    # Check for web-related keywords
    web_keywords = [
        "search", "find", "lookup", "web", "internet", "url", "fetch",
        "research", "information", "about"
    ]
    
    # Check for action-related keywords
    action_keywords = [
        "run", "execute", "command", "service", "system", "check",
        "start", "stop", "restart", "status"
    ]
    
    # Check for complex task indicators
    complex_indicators = [
        "refactor", "migrate", "implement", "add authentication",
        "add feature", "restructure", "redesign"
    ]
    
    # Classify intent
    if any(keyword in user_lower for keyword in complex_indicators):
        intent: Literal["chat", "code", "web", "action", "complex"] = "complex"
        mode: Literal["simple", "planning", "execution"] = "planning"
    elif any(keyword in user_lower for keyword in code_keywords):
        intent = "code"
        mode = "planning" if len(user_message.split()) > 10 else "simple"
    elif any(keyword in user_lower for keyword in web_keywords):
        intent = "web"
        mode = "simple"
    elif any(keyword in user_lower for keyword in action_keywords):
        intent = "action"
        mode = "simple"
    else:
        intent = "chat"
        mode = "simple"
    
    state["intent"] = intent
    state["mode"] = mode
    
    return state

