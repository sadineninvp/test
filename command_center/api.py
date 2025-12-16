"""
FastAPI server for Command Center
Supports both Phase 2 (hardcoded) and Phase 3 (LLM) modes
"""

import os
import uuid
from fastapi import FastAPI, HTTPException, Query, Cookie
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

from .command_center import CommandCenter  # Phase 2
from .llm_command_center import LLMCommandCenter  # Phase 3
from .conversation_state import ConversationState
from action_agent import StateManager

app = FastAPI(
    title="IQIDE Command Center API",
    description="Command Center with Phase 2 (hardcoded) and Phase 3 (LLM) support",
    version="0.3.0"
)

# Session storage (in-memory, per-process)
# In production, use Redis or database for persistence
_sessions: dict = {}  # {session_id: {"v2": CommandCenter, "v3": LLMCommandCenter, "state_manager": StateManager, "conversation_state": ConversationState}}


def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, dict]:
    """
    Get or create a session
    
    Returns:
        Tuple of (session_id, session_data)
    """
    if not session_id or session_id not in _sessions:
        # Create new session
        session_id = str(uuid.uuid4())
        state_manager = StateManager(session_id=session_id)
        conversation_state = ConversationState(session_id=session_id)
        _sessions[session_id] = {
            "v2": None,  # Lazy init
            "v3": None,  # Lazy init
            "state_manager": state_manager,
            "conversation_state": conversation_state
        }
    
    return session_id, _sessions[session_id]


# Initialize Command Centers (legacy, without session)
command_center_v2 = CommandCenter()  # Phase 2: Hardcoded
command_center_v3: Optional[LLMCommandCenter] = None  # Phase 3: LLM (lazy init)


def get_command_center_v3(session_data: Optional[dict] = None) -> LLMCommandCenter:
    """Get or create Phase 3 Command Center"""
    global command_center_v3
    
    # If session_data provided, use session-specific center
    if session_data:
        if session_data["v3"] is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=500,
                    detail="OPENAI_API_KEY environment variable not set. Phase 3 requires OpenAI API key."
                )
            state_manager = session_data["state_manager"]
            conversation_state = session_data["conversation_state"]
            session_data["v3"] = LLMCommandCenter(
                api_key=api_key,
                executor=None,  # Will create with state_manager
                service_manager=None,
                web_tools=None,
                file_tools=None,
                conversation_state=conversation_state
            )
            # Update executor to use state_manager
            from action_agent import CommandExecutor
            session_data["v3"].function_caller.executor = CommandExecutor(
                state_manager=state_manager
            )
        return session_data["v3"]
    
    # Legacy: global instance (no session)
    if command_center_v3 is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY environment variable not set. Phase 3 requires OpenAI API key."
            )
        command_center_v3 = LLMCommandCenter(api_key=api_key)
    return command_center_v3


class ExecuteRequest(BaseModel):
    """Request model for execute endpoint"""
    request: str
    use_llm: Optional[bool] = False  # If True, use Phase 3 (LLM), else Phase 2 (hardcoded)
    autonomous: Optional[bool] = False  # If True, use Phase 5 (Autonomous Agent)


class ExecuteResponse(BaseModel):
    """Response model for execute endpoint"""
    success: bool
    message: str
    data: dict
    original_request: str
    mode: str  # "phase2" or "phase3"
    session_id: Optional[str] = None  # Session ID for state persistence


@app.get("/")
async def root():
    """Root endpoint"""
    has_llm = bool(os.getenv("OPENAI_API_KEY"))
    
    return {
        "name": "IQIDE Command Center",
        "version": "0.3.0",
        "modes": {
            "phase2": "Hardcoded routing (always available)",
            "phase3": f"LLM-powered routing ({'available' if has_llm else 'requires OPENAI_API_KEY'})",
            "phase5": f"Autonomous Agent ({'available' if has_llm else 'requires OPENAI_API_KEY'})"
        },
        "endpoints": {
            "/api/execute": "POST - Execute a command (use_llm/autonomous parameters to choose mode)",
            "/api/supported-actions": "GET - List supported actions (Phase 2 only)",
            "/api/tools": "GET - List available tools (Phase 3 only)",
            "/api/approve": "POST - Approve pending operation (Phase 5 only)"
        }
    }


@app.post("/api/execute", response_model=ExecuteResponse)
async def execute(
    request: ExecuteRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None)
):
    """
    Execute a user request
    
    Args:
        request: ExecuteRequest with user's natural language request and mode choice
        response: FastAPI Response object (to set cookies)
        session_id: Session ID from cookie (optional)
        
    Returns:
        ExecuteResponse with execution result and session_id
    """
    if not request.request or not request.request.strip():
        raise HTTPException(status_code=400, detail="Request cannot be empty")
    
    try:
        # Get or create session
        session_id, session_data = get_or_create_session(session_id)
        
        # Set session cookie
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        
        if request.autonomous:
            # Phase 5: Autonomous Agent (LangGraph)
            try:
                from .autonomous.graph.graph import create_autonomous_agent_graph
                from .autonomous.utils.checkpointer import get_checkpointer
                from .autonomous.graph.state import from_conversation_state
                from langchain_core.messages import HumanMessage
                
                # Create graph
                graph = create_autonomous_agent_graph()
                checkpointer = get_checkpointer()
                compiled_graph = graph.compile(checkpointer=checkpointer)
                
                # Prepare initial state
                conversation_state = session_data.get("conversation_state")
                state_manager = session_data.get("state_manager")
                initial_state = from_conversation_state(
                    conversation_state,
                    state_manager,
                    session_id
                )
                
                # Add user message
                initial_state["messages"] = [HumanMessage(content=request.request)]
                
                # Thread config for checkpointing
                thread_config = {"configurable": {"thread_id": session_id}}
                
                # Invoke graph
                final_state = compiled_graph.invoke(initial_state, config=thread_config)
                
                # Extract result
                summary = final_state.get("summary", "")
                if not summary:
                    # Get last assistant message
                    messages = final_state.get("messages", [])
                    for msg in reversed(messages):
                        if isinstance(msg, dict) and msg.get("role") == "assistant":
                            summary = msg.get("content", "")
                            break
                        elif hasattr(msg, "content"):
                            summary = msg.content
                            break
                
                result = {
                    "success": len(final_state.get("errors", [])) == 0,
                    "message": summary or "Task completed",
                    "data": {
                        "created_files": final_state.get("created_files", []),
                        "modified_files": final_state.get("modified_files", []),
                        "verification_results": final_state.get("verification_results"),
                        "plan": final_state.get("plan"),
                        "errors": final_state.get("errors", [])
                    },
                    "original_request": request.request,
                    "mode": "autonomous",
                    "session_id": session_id
                }
                
                return ExecuteResponse(**result)
                
            except ImportError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Autonomous agent not available. Install dependencies: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Autonomous agent error: {str(e)}"
                )
        elif request.use_llm:
            # Phase 3: LLM-powered with session
            center = get_command_center_v3(session_data=session_data)
            result = center.handle(request.request)
            result["mode"] = "phase3"
            result["session_id"] = session_id
            return ExecuteResponse(**result)
        else:
            # Phase 2: Hardcoded routing (legacy, no session state)
            result = command_center_v2.handle(request.request)
            result["mode"] = "phase2"
            result["session_id"] = session_id
            return ExecuteResponse(**result)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/supported-actions")
async def get_supported_actions():
    """Get list of supported action types (Phase 2 only)"""
    return {
        "mode": "phase2",
        "supported_actions": command_center_v2.get_supported_actions(),
        "description": "These are the action types the Command Center can handle (hardcoded patterns)"
    }


@app.get("/api/tools")
async def get_tools():
    """Get list of available tools (Phase 3 only)"""
    try:
        center = get_command_center_v3()
        return {
            "mode": "phase3",
            "available_tools": center.get_available_tools(),
            "description": "These are the tools available to the LLM"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/approve")
async def approve_operation(
    approval_id: str,
    approved: bool,
    session_id: Optional[str] = Cookie(None)
):
    """
    Approve or reject a pending operation (Human-in-the-Loop)
    
    Args:
        approval_id: Approval request ID
        approved: True to approve, False to reject
        session_id: Session ID from cookie
        
    Returns:
        Status of approval
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    try:
        from .autonomous.graph.graph import create_autonomous_agent_graph
        from .autonomous.utils.checkpointer import get_checkpointer
        
        # Create graph
        graph = create_autonomous_agent_graph()
        checkpointer = get_checkpointer()
        compiled_graph = graph.compile(checkpointer=checkpointer)
        
        # Thread config
        thread_config = {"configurable": {"thread_id": session_id}}
        
        # Load current state
        current_state = compiled_graph.get_state(thread_config)
        
        if not current_state or not current_state.values:
            raise HTTPException(status_code=404, detail="No pending operation found")
        
        state_values = current_state.values
        
        # Update approval status
        state_values["approval_status"] = "approved" if approved else "rejected"
        state_values["requires_approval"] = False
        
        # Update state
        compiled_graph.update_state(thread_config, state_values)
        
        # Resume execution if approved
        if approved:
            # The graph will resume from HIL node
            result = compiled_graph.invoke(None, config=thread_config)
            return {
                "success": True,
                "message": "Operation approved and resumed",
                "approved": True
            }
        else:
            return {
                "success": True,
                "message": "Operation rejected",
                "approved": False
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing approval: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
