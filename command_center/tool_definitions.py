"""
Tool Definitions - Define Action Agent functions as LLM tools
Maps Action Agent functions to OpenAI function calling format
"""

from typing import List, Dict, Any


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get tool definitions for LLM function calling
    These define what functions the LLM can call
    
    Returns:
        List of function definitions in OpenAI format
    """
    return [
        {
            "name": "run_command",
            "description": "Execute a shell command and return the output. Use this for running any terminal commands like 'ls', 'whoami', 'ps', etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute (e.g., 'ls -la', 'whoami', 'ps aux')"
                    }
                },
                "required": ["command"]
            }
        },
        {
            "name": "check_service",
            "description": "Check the status of a system service. Returns whether the service is running, stopped, or failed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service to check (e.g., 'nginx', 'apache2', 'docker')"
                    }
                },
                "required": ["service_name"]
            }
        },
        {
            "name": "start_service",
            "description": "Start a system service. Use this when you need to start a stopped service.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service to start (e.g., 'nginx', 'apache2', 'docker')"
                    }
                },
                "required": ["service_name"]
            }
        },
        {
            "name": "stop_service",
            "description": "Stop a running system service. Use this when you need to stop a service.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service to stop (e.g., 'nginx', 'apache2', 'docker')"
                    }
                },
                "required": ["service_name"]
            }
        },
        {
            "name": "restart_service",
            "description": "Restart a system service. This will stop and then start the service. Use this when you need to restart a service to apply changes or fix issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service to restart (e.g., 'nginx', 'apache2', 'docker')"
                    }
                },
                "required": ["service_name"]
            }
        },
        {
            "name": "get_system_info",
            "description": "Get basic system information like OS, platform, machine architecture. Use this when the user asks about system details.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "web_search",
            "description": "Search the web for information. Use this when the user asks about current events, facts, news, or any information that requires up-to-date data from the internet. Returns search results with titles, snippets, and URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string (e.g., 'latest Python version', 'current president of USA', 'weather in San Francisco')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "fetch_url",
            "description": "Fetch and extract text content from a webpage URL. Use this when you need to read the full content of a webpage, especially after finding relevant URLs from web_search. The content is extracted and cleaned for easy reading.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch (must start with http:// or https://)"
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "change_directory",
            "description": "Change the current working directory. This affects all subsequent commands until changed again. Use this when the user asks to navigate to a different directory, go into a folder, or change directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to change to. Can be absolute (e.g., '/Users/name/Documents') or relative (e.g., '../parent' or 'subfolder')"
                    }
                },
                "required": ["path"]
            }
        },
        {
            "name": "get_current_directory",
            "description": "Get the current working directory. Use this when the user asks 'what directory am I in?', 'where am I?', or 'what is the current directory?'. Returns the absolute path of the current working directory.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "read_file",
            "description": "Read a file and return its contents. For code files (Python, JavaScript, etc.), also provides structure analysis including functions, classes, and imports. Use this when the user asks to 'show', 'view', 'read', 'see', or 'display' a file. The structure analysis helps understand code patterns. IMPORTANT: If the user says 'it', 'that file', or references a file without a path, check the context - it likely refers to the last file you showed them.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file (absolute or relative to current directory). If user says 'it' or 'that file', check the context provided at the start of the request - it will tell you the last file shown."
                    },
                    "analyze_structure": {
                        "type": "boolean",
                        "description": "Whether to analyze code structure (default: true for code files). Set to false if you only need raw content.",
                        "default": True
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write content to a file. Can create new files or overwrite existing ones. Use this when the user asks to 'write', 'create', 'save', or 'add to' a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file (absolute or relative to current directory)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "append": {
                        "type": "boolean",
                        "description": "If true, append to file; if false, overwrite (default: false)",
                        "default": False
                    }
                },
                "required": ["file_path", "content"]
            }
        },
        {
            "name": "list_files",
            "description": "List files and directories in a directory. Returns file names and basic info (whether each item is a file or directory). Use this when the user asks to 'list', 'show files', or 'what's in' a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path (defaults to current directory if not specified)"
                    }
                },
                "required": []
            }
        }
    ]


def get_tool_name_to_function_map() -> Dict[str, str]:
    """
    Map LLM tool names to Action Agent function names
    
    Returns:
        Dict mapping tool name to function name
    """
    return {
        "run_command": "run_command",
        "check_service": "check_service",
        "start_service": "start_service",
        "stop_service": "stop_service",
        "restart_service": "restart_service",
        "get_system_info": "get_system_info",
        "web_search": "web_search",
        "fetch_url": "fetch_url",
        "change_directory": "change_directory",
        "get_current_directory": "get_current_directory",
        "read_file": "read_file",
        "write_file": "write_file",
        "list_files": "list_files"
    }

