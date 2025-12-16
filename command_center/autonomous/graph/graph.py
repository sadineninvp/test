"""
Main Graph Construction
Creates the LangGraph state graph for autonomous agent
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from ..nodes import (
    ingress_node,
    router_node,
    planner_node,
    agent_node,
    verify_node,
    summarize_node,
    hil_node
)
from ..nodes.tools import (
    code_tools_node,
    web_tools_node,
    action_tools_node
)
from ..nodes.agents import chat_agent_node
from .edges import (
    route_by_intent,
    route_to_tools,
    check_approval_needed,
    check_approval_status
)


def create_autonomous_agent_graph():
    """
    Create the main autonomous agent graph
    
    Returns:
        Compiled LangGraph StateGraph
    """
    # Create graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("ingress", ingress_node)
    graph.add_node("router", router_node)
    graph.add_node("chat_agent", chat_agent_node)
    graph.add_node("planner", planner_node)
    graph.add_node("agent", agent_node)
    graph.add_node("code_tools", code_tools_node)
    graph.add_node("web_tools", web_tools_node)
    graph.add_node("action_tools", action_tools_node)
    graph.add_node("verify", verify_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("hil", hil_node)
    
    # Set entry point
    graph.set_entry_point("ingress")
    
    # Add edges
    graph.add_edge("ingress", "router")
    
    # Router conditional edges
    graph.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "chat_agent": "chat_agent",
            "planner": "planner",
            "agent": "agent"
        }
    )
    
    # Planner → Agent
    graph.add_edge("planner", "agent")
    
    # Chat agent → END
    graph.add_edge("chat_agent", END)
    
    # Agent → Tools (conditional)
    graph.add_conditional_edges(
        "agent",
        route_to_tools,
        {
            "code_tools": "code_tools",
            "web_tools": "web_tools",
            "action_tools": "action_tools",
            "verify": "verify",
            "done": "verify"
        }
    )
    
    # Tools → Agent (loop back)
    graph.add_edge("code_tools", "agent")
    graph.add_edge("web_tools", "agent")
    graph.add_edge("action_tools", "agent")
    
    # Verify → HIL or Summarize
    graph.add_conditional_edges(
        "verify",
        check_approval_needed,
        {
            "hil": "hil",
            "summarize": "summarize"
        }
    )
    
    # HIL → Summarize or END (if pending)
    graph.add_conditional_edges(
        "hil",
        check_approval_status,
        {
            "summarize": "summarize",
            "agent": "agent",  # Retry if rejected
            "end": END  # Wait for approval
        }
    )
    
    # Summarize → END
    graph.add_edge("summarize", END)
    
    return graph

