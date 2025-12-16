"""
Planner Node - Creates multi-step plans for complex tasks
"""

from typing import Dict, Any
from ..graph.state import AgentState
from ..utils.llm_client import get_llm_client
from langchain_core.prompts import ChatPromptTemplate


def planner_node(state: AgentState) -> AgentState:
    """
    Planner node - Creates a multi-step plan for complex tasks
    
    Args:
        state: AgentState
        
    Returns:
        Updated AgentState with plan
    """
    # Only plan if mode is "planning"
    if state.get("mode") != "planning":
        return state
    
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
        llm = get_llm_client()
        
        # Create planning prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a planning assistant. Break down tasks into clear, executable steps.
            
Create a plan with these steps. Each step should be:
- Specific and actionable
- Have clear dependencies (if any)
- Be executable independently when possible

Return the plan as a JSON structure with steps."""),
            ("user", "Task: {task}\n\nCreate a step-by-step plan to accomplish this task.")
        ])
        
        chain = prompt | llm
        
        response = chain.invoke({"task": user_message})
        plan_text = response.content if hasattr(response, "content") else str(response)
        
        # Parse plan (simple extraction - can be enhanced)
        # For now, create a simple plan structure
        steps = []
        lines = plan_text.split("\n")
        step_num = 1
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                # Extract step description
                step_desc = line.lstrip("0123456789.-* ").strip()
                if step_desc:
                    steps.append({
                        "id": step_num,
                        "action": step_desc,
                        "status": "pending",
                        "dependencies": []
                    })
                    step_num += 1
        
        # If no steps extracted, create a simple plan
        if not steps:
            steps = [
                {"id": 1, "action": "Understand the task", "status": "pending", "dependencies": []},
                {"id": 2, "action": "Execute the task", "status": "pending", "dependencies": [1]},
                {"id": 3, "action": "Verify completion", "status": "pending", "dependencies": [2]},
            ]
        
        # Store plan
        state["plan"] = {
            "task": user_message,
            "steps": steps,
            "total_steps": len(steps)
        }
        state["steps"] = steps
        state["current_step"] = 0
        
    except Exception as e:
        # If planning fails, create a simple plan
        state["plan"] = {
            "task": user_message,
            "steps": [
                {"id": 1, "action": "Execute task", "status": "pending", "dependencies": []}
            ],
            "total_steps": 1
        }
        state["steps"] = state["plan"]["steps"]
        state["current_step"] = 0
        state["errors"] = state.get("errors", []) + [f"Planning error: {str(e)}"]
    
    return state

