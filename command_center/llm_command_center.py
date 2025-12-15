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
from .conversation_state import ConversationState
from action_agent import WebTools, FileTools


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
        web_tools=None,
        file_tools=None,
        conversation_state=None
    ):
        """
        Initialize LLM Command Center
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: LLM model name
            executor: CommandExecutor instance (creates new if not provided)
            service_manager: ServiceManager instance (creates new if not provided)
            web_tools: WebTools instance (creates new if not provided)
            file_tools: FileTools instance (creates new if not provided)
            conversation_state: ConversationState instance (creates new if not provided)
        """
        self.llm_client = LLMClient(api_key=api_key, model=model)
        self.conversation_state = conversation_state or ConversationState()
        self.function_caller = FunctionCaller(
            executor=executor,
            service_manager=service_manager,
            web_tools=web_tools,
            file_tools=file_tools
        )
        self.formatter = ResultFormatter()
        self.tools = get_tool_definitions()
        
        # System prompt for the LLM
        self.system_prompt = """You are a helpful coding assistant that can execute system commands, manage services, and work with files on a computer.

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
- For test files, you can see all test functions (test_1, test_2, etc.)
- When users reference "it" or "that file", they mean the last file you showed them
- Remember files you've read in this conversation
- When asked to edit code, suggest specific code that follows existing patterns

CONTEXT AWARENESS:
- Pay attention to context provided at the start of requests
- "Last file shown" tells you what file the user is referring to
- "Current directory" tells you where you are
- Use this context to understand ambiguous requests like "add test 6 to it"

When a user makes a request:
1. Understand what they want to accomplish
2. Use context to resolve references ("it", "that file", etc.)
3. Use the available tools to perform the actions
4. For code edits, reference the structure you've seen and follow existing patterns
5. Provide clear, helpful responses based on the tool results

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
        # Get context from conversation state
        context = self.conversation_state.get_context_for_llm()
        
        # Enhance request with context if available
        if context:
            enhanced_request = f"{context}\n\nUser request: {request}"
        else:
            enhanced_request = request
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": enhanced_request}
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
                
                # Update conversation state based on tool calls
                self._update_conversation_state(tool_calls, function_results)
                
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
    
    def _update_conversation_state(self, tool_calls: List[Dict[str, Any]], function_results: List[Dict[str, Any]]):
        """
        Update conversation state based on executed tool calls
        
        Args:
            tool_calls: List of tool calls from LLM
            function_results: List of function execution results
        """
        for i, tool_call in enumerate(tool_calls):
            if i < len(function_results):
                func_result = function_results[i]
                function_name = tool_call.get("function", {}).get("name", "")
                arguments = tool_call.get("function", {}).get("arguments", "{}")
                
                try:
                    import json
                    if isinstance(arguments, str):
                        args = json.loads(arguments)
                    else:
                        args = arguments
                    
                    # Update state based on function called
                    if function_name == "read_file" and func_result.get("success"):
                        file_path = args.get("file_path", "")
                        result_data = func_result.get("result", {})
                        content = result_data.get("content", "")
                        structure = result_data.get("structure")
                        self.conversation_state.update_file_shown(
                            file_path=file_path,
                            content=content,
                            structure=structure
                        )
                    
                    elif function_name == "change_directory" and func_result.get("success"):
                        result_data = func_result.get("result", {})
                        directory = result_data.get("directory", "")
                        if directory:
                            self.conversation_state.update_directory(directory)
                    
                    elif function_name == "run_command":
                        command = args.get("command", "")
                        if command:
                            self.conversation_state.add_command(command)
                            
                except Exception:
                    # Ignore errors in state updates
                    pass

