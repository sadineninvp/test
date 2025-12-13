"""
FastAPI server for Command Center
Supports both Phase 2 (hardcoded) and Phase 3 (LLM) modes
"""

import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from .command_center import CommandCenter  # Phase 2
from .llm_command_center import LLMCommandCenter  # Phase 3

app = FastAPI(
    title="IQIDE Command Center API",
    description="Command Center with Phase 2 (hardcoded) and Phase 3 (LLM) support",
    version="0.3.0"
)

# Initialize Command Centers
command_center_v2 = CommandCenter()  # Phase 2: Hardcoded
command_center_v3: Optional[LLMCommandCenter] = None  # Phase 3: LLM (lazy init)


def get_command_center_v3() -> LLMCommandCenter:
    """Get or create Phase 3 Command Center"""
    global command_center_v3
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


class ExecuteResponse(BaseModel):
    """Response model for execute endpoint"""
    success: bool
    message: str
    data: dict
    original_request: str
    mode: str  # "phase2" or "phase3"


@app.get("/")
async def root():
    """Root endpoint"""
    has_llm = bool(os.getenv("OPENAI_API_KEY"))
    
    return {
        "name": "IQIDE Command Center",
        "version": "0.3.0",
        "modes": {
            "phase2": "Hardcoded routing (always available)",
            "phase3": f"LLM-powered routing ({'available' if has_llm else 'requires OPENAI_API_KEY'})"
        },
        "endpoints": {
            "/api/execute": "POST - Execute a command (use_llm parameter to choose mode)",
            "/api/supported-actions": "GET - List supported actions (Phase 2 only)",
            "/api/tools": "GET - List available tools (Phase 3 only)"
        }
    }


@app.post("/api/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """
    Execute a user request
    
    Args:
        request: ExecuteRequest with user's natural language request and mode choice
        
    Returns:
        ExecuteResponse with execution result
    """
    if not request.request or not request.request.strip():
        raise HTTPException(status_code=400, detail="Request cannot be empty")
    
    try:
        if request.use_llm:
            # Phase 3: LLM-powered
            center = get_command_center_v3()
            result = center.handle(request.request)
            result["mode"] = "phase3"
            return ExecuteResponse(**result)
        else:
            # Phase 2: Hardcoded routing
            result = command_center_v2.handle(request.request)
            result["mode"] = "phase2"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
