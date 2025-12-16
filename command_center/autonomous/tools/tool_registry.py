"""
Tool Registry - Registers all available tools
Wraps existing Action Agent tools as LangChain tools
"""

from langchain_core.tools import tool
from typing import List
from langchain_core.tools import BaseTool

# Import existing Action Agent tools
from action_agent import CommandExecutor, ServiceManager, WebTools, FileTools


# Initialize tool instances (will be created on first use)
_executor = None
_service_manager = None
_web_tools = None
_file_tools = None


def _get_executor():
    global _executor
    if _executor is None:
        _executor = CommandExecutor()
    return _executor


def _get_service_manager():
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager


def _get_web_tools():
    global _web_tools
    if _web_tools is None:
        _web_tools = WebTools()
    return _web_tools


def _get_file_tools():
    global _file_tools
    if _file_tools is None:
        _file_tools = FileTools()
    return _file_tools


# Code Tools
@tool
def read_file(file_path: str, analyze_structure: bool = True) -> dict:
    """Read a file and return its contents. For code files, also provides structure analysis."""
    return _get_file_tools().read_file(file_path, analyze_structure)


@tool
def write_file(file_path: str, content: str, append: bool = False) -> dict:
    """Write content to a file. Can create new files or overwrite existing ones."""
    return _get_file_tools().write_file(file_path, content, append)


@tool
def list_files(directory: str = None) -> dict:
    """List files and directories in a directory."""
    return _get_file_tools().list_files(directory)


# Web Tools
@tool
def web_search(query: str, max_results: int = 5) -> dict:
    """Search the web for information."""
    return _get_web_tools().web_search(query, max_results)


@tool
def fetch_url(url: str) -> dict:
    """Fetch and extract text content from a webpage URL."""
    return _get_web_tools().fetch_url(url)


# Action Tools
@tool
def run_command(command: str) -> dict:
    """Execute a shell command and return the output."""
    return _get_executor().run(command)


@tool
def check_service(service_name: str) -> dict:
    """Check the status of a system service."""
    return _get_service_manager().check_service(service_name)


@tool
def start_service(service_name: str) -> dict:
    """Start a system service."""
    return _get_service_manager().start_service(service_name)


@tool
def stop_service(service_name: str) -> dict:
    """Stop a system service."""
    return _get_service_manager().stop_service(service_name)


@tool
def restart_service(service_name: str) -> dict:
    """Restart a system service."""
    return _get_service_manager().restart_service(service_name)


@tool
def get_system_info() -> dict:
    """Get basic system information."""
    return _get_executor().get_system_info()


@tool
def change_directory(path: str) -> dict:
    """Change the current working directory."""
    return _get_executor().change_directory(path)


@tool
def get_current_directory() -> dict:
    """Get the current working directory."""
    return _get_executor().get_current_directory()


def get_code_tools() -> List[BaseTool]:
    """Get code-related tools"""
    return [read_file, write_file, list_files]


def get_web_tools() -> List[BaseTool]:
    """Get web-related tools"""
    return [web_search, fetch_url]


def get_action_tools() -> List[BaseTool]:
    """Get action-related tools"""
    return [
        run_command,
        check_service,
        start_service,
        stop_service,
        restart_service,
        get_system_info,
        change_directory,
        get_current_directory,
    ]


def get_tools() -> List[BaseTool]:
    """Get all available tools"""
    return get_code_tools() + get_web_tools() + get_action_tools()

