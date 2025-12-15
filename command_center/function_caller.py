"""
Function Caller - Execute LLM function calls by calling Action Agent functions
"""

import json
from typing import Dict, Any, Optional, Callable, List

from action_agent import CommandExecutor, ServiceManager, WebTools, FileTools
from .tool_definitions import get_tool_name_to_function_map


class FunctionCaller:
    """
    Executes LLM function calls by mapping to Action Agent functions
    """
    
    def __init__(
        self,
        executor: Optional[CommandExecutor] = None,
        service_manager: Optional[ServiceManager] = None,
        web_tools: Optional[WebTools] = None,
        file_tools: Optional[FileTools] = None
    ):
        """
        Initialize function caller
        
        Args:
            executor: CommandExecutor instance
            service_manager: ServiceManager instance
            web_tools: WebTools instance
            file_tools: FileTools instance
        """
        self.executor = executor or CommandExecutor()
        self.service_manager = service_manager or ServiceManager(executor=self.executor)
        self.web_tools = web_tools or WebTools()
        self.file_tools = file_tools or FileTools()
        self.tool_map = get_tool_name_to_function_map()
        
        # Map tool names to actual functions
        self.function_map: Dict[str, Callable] = {
            "run_command": self.executor.run,
            "check_service": self.service_manager.check_service,
            "start_service": self.service_manager.start_service,
            "stop_service": self.service_manager.stop_service,
            "restart_service": self.service_manager.restart_service,
            "get_system_info": self.executor.get_system_info,
            "web_search": self.web_tools.web_search,
            "fetch_url": self.web_tools.fetch_url,
            "change_directory": self.executor.change_directory,
            "get_current_directory": self.executor.get_current_directory,
            "read_file": self.file_tools.read_file,
            "write_file": self.file_tools.write_file,
            "list_files": self.file_tools.list_files,
        }
    
    def call_function(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call from LLM
        
        Args:
            tool_call: Dict with 'function' key containing 'name' and 'arguments'
            
        Returns:
            Dict with execution result
        """
        function_name = tool_call.get("function", {}).get("name")
        arguments_str = tool_call.get("function", {}).get("arguments", "{}")
        
        if not function_name:
            return {
                "success": False,
                "error": "Function name not provided",
                "result": None
            }
        
        # Map tool name to function name
        mapped_name = self.tool_map.get(function_name, function_name)
        
        if mapped_name not in self.function_map:
            return {
                "success": False,
                "error": f"Unknown function: {function_name}",
                "result": None
            }
        
        # Parse arguments
        try:
            if isinstance(arguments_str, str):
                arguments = json.loads(arguments_str)
            else:
                arguments = arguments_str
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON arguments: {str(e)}",
                "result": None
            }
        
        # Get the function
        func = self.function_map[mapped_name]
        
        # Call the function with arguments
        try:
            # Handle different argument patterns
            if isinstance(arguments, dict):
                if "command" in arguments:
                    result = func(arguments["command"])
                elif "service_name" in arguments:
                    result = func(arguments["service_name"])
                elif "query" in arguments:
                    # Web search with optional max_results
                    max_results = arguments.get("max_results", 5)
                    result = func(arguments["query"], max_results=max_results)
                elif "url" in arguments:
                    result = func(arguments["url"])
                elif "path" in arguments:
                    # change_directory
                    result = func(arguments["path"])
                elif "file_path" in arguments:
                    # read_file or write_file
                    if "content" in arguments:
                        # write_file
                        result = func(
                            arguments["file_path"],
                            arguments["content"],
                            arguments.get("append", False)
                        )
                    else:
                        # read_file
                        result = func(
                            arguments["file_path"],
                            arguments.get("analyze_structure", True)
                        )
                elif "directory" in arguments:
                    # list_files with directory specified
                    result = func(arguments["directory"])
                elif len(arguments) == 0:
                    # No arguments (e.g., get_system_info, get_current_directory, list_files)
                    result = func()
                else:
                    # Try calling with **arguments
                    result = func(**arguments)
            else:
                # Arguments is a single value
                result = func(arguments)
            
            return {
                "success": True,
                "function_name": function_name,
                "arguments": arguments,
                "result": result,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "function_name": function_name,
                "arguments": arguments,
                "result": None,
                "error": str(e)
            }
    
    def call_functions(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple function calls
        
        Args:
            tool_calls: List of tool call dicts
            
        Returns:
            List of execution results
        """
        results = []
        for tool_call in tool_calls:
            result = self.call_function(tool_call)
            results.append(result)
        return results

