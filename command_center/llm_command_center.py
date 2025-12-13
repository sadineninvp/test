"""
LLM-Powered Command Center - Phase 3
Uses LLM for understanding requests and function calling
"""

import json
from typing import Dict, Any, Optional, List

from .llm_client import LLMClient
from .tool_definitions import get_tool_definitions
from .function_caller import FunctionCaller
from .formatter import ResultFormatter
from action_agent import WebTools


class LLMCommandCenter:
    """
    Command Center powered by LLM function calling
    Replaces hardcoded routing with AI understanding
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        executor=None,
        service_manager=None,
        web_tools=None
    ):
        """
        Initialize LLM Command Center
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: LLM model name
            executor: CommandExecutor instance (creates new if not provided)
            service_manager: ServiceManager instance (creates new if not provided)
            web_tools: WebTools instance (creates new if not provided)
        """
        self.llm_client = LLMClient(api_key=api_key, model=model)
        self.function_caller = FunctionCaller(
            executor=executor,
            service_manager=service_manager,
            web_tools=web_tools
        )
        self.formatter = ResultFormatter()
        self.tools = get_tool_definitions()
        
        # System prompt for the LLM
        self.system_prompt = """You are a helpful assistant that can execute system commands and manage services on a computer.

You have access to tools that allow you to:
- Run shell commands
- Check, start, stop, and restart system services
- Get system information

When a user makes a request:
1. Understand what they want to accomplish
2. Use the available tools to perform the actions
3. Provide clear, helpful responses based on the tool results

Always be helpful and explain what you're doing. If a tool call fails, explain why and suggest alternatives.
"""
    
    def handle(self, request: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Handle a user request using LLM function calling
        
        Args:
            request: User's natural language request
            max_iterations: Maximum number of LLM/function call iterations
            
        Returns:
            Dict with:
                - success: bool
                - message: str (formatted response)
                - data: Dict (execution details)
                - original_request: str
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": request}
        ]
        
        tool_results = []
        iterations = 0
        
        try:
            while iterations < max_iterations:
                iterations += 1
                
                # Get LLM response with function calling
                response = self.llm_client.chat_with_functions(
                    messages=messages,
                    functions=self.tools,
                    function_call="auto"
                )
                
                # Check for errors
                if "error" in response:
                    return {
                        "success": False,
                        "message": f"LLM Error: {response['error']}",
                        "data": {"error": response["error"]},
                        "original_request": request
                    }
                
                # Add LLM response to messages
                assistant_message = {
                    "role": "assistant",
                    "content": response.get("content")
                }
                if response.get("tool_calls"):
                    assistant_message["tool_calls"] = response["tool_calls"]
                
                messages.append(assistant_message)
                
                # Check if LLM wants to call functions
                tool_calls = response.get("tool_calls", [])
                
                if not tool_calls:
                    # No function calls, LLM is done
                    final_message = response.get("content", "No response from LLM")
                    return {
                        "success": True,
                        "message": final_message,
                        "data": {
                            "iterations": iterations,
                            "tool_results": tool_results,
                            "llm_response": response
                        },
                        "original_request": request
                    }
                
                # Execute function calls
                function_results = self.function_caller.call_functions(tool_calls)
                tool_results.extend(function_results)
                
                # Prepare tool response messages for LLM
                tool_messages = []
                for i, tool_call in enumerate(tool_calls):
                    func_result = function_results[i] if i < len(function_results) else {}
                    
                    # Format result for LLM
                    if func_result.get("success"):
                        result_content = json.dumps(func_result.get("result"), indent=2, default=str)
                    else:
                        result_content = f"Error: {func_result.get('error', 'Unknown error')}"
                    
                    tool_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "content": result_content
                    })
                
                messages.extend(tool_messages)
            
            # Max iterations reached
            return {
                "success": False,
                "message": "Maximum iterations reached. The request may be too complex.",
                "data": {
                    "iterations": iterations,
                    "tool_results": tool_results
                },
                "original_request": request
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing request: {str(e)}",
                "data": {"error": str(e)},
                "original_request": request
            }
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [tool["name"] for tool in self.tools]

