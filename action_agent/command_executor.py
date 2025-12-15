"""
Command Executor - Core module for executing system commands
"""

import subprocess
import platform
from typing import Optional, Dict, Any

from .config import DEFAULT_TIMEOUT, MAX_OUTPUT_SIZE
from .logger import ActionLogger
from .state_manager import StateManager


class CommandExecutor:
    """
    Executes shell commands safely with logging and error handling
    """
    
    def __init__(
        self,
        logger: Optional[ActionLogger] = None,
        timeout: int = DEFAULT_TIMEOUT,
        state_manager: Optional[StateManager] = None
    ):
        """
        Initialize command executor
        
        Args:
            logger: ActionLogger instance (creates new one if not provided)
            timeout: Default timeout for commands in seconds
            state_manager: StateManager instance (creates new one if not provided)
        """
        self.logger = logger or ActionLogger()
        self.timeout = timeout
        self.system = platform.system()  # 'Darwin', 'Linux', 'Windows'
        self.state_manager = state_manager or StateManager()
    
    def run(
        self,
        command: str,
        timeout: Optional[int] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        use_state_directory: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a shell command and return results
        
        Args:
            command: Command string to execute
            timeout: Timeout in seconds (uses instance default if not provided)
            cwd: Working directory for command execution (if None and use_state_directory=True, uses tracked directory)
            env: Environment variables (dict)
            use_state_directory: If True and cwd is None, use tracked directory from StateManager
            
        Returns:
            Dict with keys:
                - success: bool
                - output: str (stdout)
                - error: str (stderr)
                - return_code: int
                - command: str (echo of command)
        """
        timeout = timeout or self.timeout
        start_time = None
        
        try:
            import time
            start_time = time.time()
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env
            )
            
            # Truncate output if too large
            output = result.stdout[:MAX_OUTPUT_SIZE] if result.stdout else ""
            error = result.stderr[:MAX_OUTPUT_SIZE] if result.stderr else ""
            
            # Determine success (exit code 0 or non-zero with output is often OK)
            success = result.returncode == 0 or (result.returncode != 0 and output)
            
            # Calculate execution time
            execution_time = time.time() - start_time if start_time else 0
            
            response = {
                "success": success,
                "output": output,
                "error": error,
                "return_code": result.returncode,
                "command": command,
                "execution_time": execution_time
            }
            
            # Log the action
            self.logger.log(
                action_type="command",
                action=command,
                result=output[:500] if output else None,  # Truncate for logging
                success=success,
                error_message=error if not success and error else None,
                metadata={
                    "return_code": result.returncode,
                    "execution_time": execution_time,
                    "timeout": timeout
                }
            )
            
            return response
            
        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time if start_time else timeout
            
            response = {
                "success": False,
                "output": "",
                "error": f"Command timed out after {timeout} seconds",
                "return_code": -1,
                "command": command,
                "execution_time": execution_time
            }
            
            self.logger.log(
                action_type="command",
                action=command,
                result=None,
                success=False,
                error_message=f"Timeout after {timeout}s",
                metadata={"timeout": timeout, "execution_time": execution_time}
            )
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time if start_time else 0
            
            response = {
                "success": False,
                "output": "",
                "error": str(e),
                "return_code": -1,
                "command": command,
                "execution_time": execution_time
            }
            
            self.logger.log(
                action_type="command",
                action=command,
                result=None,
                success=False,
                error_message=str(e),
                metadata={"exception_type": type(e).__name__}
            )
            
            return response
    
    def run_safe(self, command: str, **kwargs) -> str:
        """
        Simplified version that returns just the output string
        Raises exception if command fails
        
        Args:
            command: Command to execute
            **kwargs: Additional arguments passed to run()
            
        Returns:
            Output string from command
            
        Raises:
            RuntimeError: If command fails
        """
        result = self.run(command, **kwargs)
        
        if not result["success"]:
            error_msg = result.get("error", "Unknown error")
            raise RuntimeError(f"Command failed: {command}\nError: {error_msg}")
        
        return result["output"]
    
    def get_system_info(self) -> Dict[str, str]:
        """
        Get basic system information
        
        Returns:
            Dict with system information
        """
        return {
            "system": self.system,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
    
    def change_directory(self, path: str) -> Dict[str, Any]:
        """
        Change the current working directory (affects future commands)
        
        Args:
            path: Path to change to (absolute or relative)
            
        Returns:
            Dict with execution result
        """
        result = self.state_manager.change_directory(path)
        
        # Log the action
        if result["success"]:
            self.logger.log(
                action_type="directory",
                action=f"change_directory('{path}')",
                result=f"Changed to: {result['directory']}",
                success=True,
                metadata={
                    "from": result.get("previous_directory"),
                    "to": result["directory"]
                }
            )
        else:
            self.logger.log(
                action_type="directory",
                action=f"change_directory('{path}')",
                result=None,
                success=False,
                error_message=result.get("error")
            )
        
        return result
    
    def get_current_directory(self) -> Dict[str, Any]:
        """
        Get the current working directory
        
        Returns:
            Dict with current directory
        """
        current_dir = self.state_manager.get_current_directory()
        
        return {
            "success": True,
            "directory": current_dir
        }

