"""
Service Manager - Manage system services
Supports systemd (Linux), launchctl (macOS), and basic Windows services
"""

import platform
import subprocess
from typing import Dict, Any, Optional

from .command_executor import CommandExecutor
from .logger import ActionLogger


class ServiceManager:
    """
    Manages system services across different operating systems
    """
    
    def __init__(self, executor: Optional[CommandExecutor] = None, logger: Optional[ActionLogger] = None):
        """
        Initialize service manager
        
        Args:
            executor: CommandExecutor instance (creates new if not provided)
            logger: ActionLogger instance (creates new if not provided)
        """
        self.executor = executor or CommandExecutor()
        self.logger = logger or ActionLogger()
        self.system = platform.system()
    
    def _get_service_command_prefix(self) -> str:
        """Get the command prefix for service management based on OS"""
        if self.system == "Linux":
            return "systemctl"
        elif self.system == "Darwin":  # macOS
            return "launchctl"
        elif self.system == "Windows":
            return "sc"  # Windows Service Controller
        else:
            return "systemctl"  # Default to systemd
    
    def check_service(self, service_name: str) -> Dict[str, Any]:
        """
        Check if a service is running and get its status
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dict with status information
        """
        if self.system == "Linux":
            result = self.executor.run(f"systemctl is-active {service_name}")
            is_active = "active" in result["output"].lower()
            
            # Get detailed status
            status_result = self.executor.run(f"systemctl status {service_name}")
            
            return {
                "service_name": service_name,
                "is_running": is_active,
                "status": "running" if is_active else "stopped",
                "details": status_result["output"][:500],  # First 500 chars
                "system": "linux"
            }
            
        elif self.system == "Darwin":  # macOS
            # Try to get service status (macOS services are more complex)
            result = self.executor.run(f"launchctl list | grep {service_name}")
            is_running = result["return_code"] == 0 and service_name in result["output"]
            
            return {
                "service_name": service_name,
                "is_running": is_running,
                "status": "running" if is_running else "stopped",
                "details": result["output"][:500],
                "system": "macos"
            }
            
        else:
            # Generic fallback - just try to find the process
            result = self.executor.run(f"pgrep -f {service_name}")
            is_running = result["return_code"] == 0
            
            return {
                "service_name": service_name,
                "is_running": is_running,
                "status": "running" if is_running else "stopped",
                "details": result["output"],
                "system": "unknown"
            }
    
    def start_service(self, service_name: str) -> Dict[str, Any]:
        """
        Start a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dict with execution result
        """
        if self.system == "Linux":
            result = self.executor.run(f"sudo systemctl start {service_name}")
        elif self.system == "Darwin":
            # macOS services usually don't need sudo, but format varies
            result = self.executor.run(f"launchctl load -w /Library/LaunchDaemons/{service_name}.plist")
        else:
            result = self.executor.run(f"service {service_name} start")
        
        success = result["return_code"] == 0
        
        # Log the action
        self.logger.log(
            action_type="service",
            action=f"start_service({service_name})",
            result="Started successfully" if success else result["error"],
            success=success,
            error_message=result["error"] if not success else None
        )
        
        return {
            "service_name": service_name,
            "action": "start",
            "success": success,
            "output": result["output"],
            "error": result["error"] if not success else None
        }
    
    def stop_service(self, service_name: str) -> Dict[str, Any]:
        """
        Stop a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dict with execution result
        """
        if self.system == "Linux":
            result = self.executor.run(f"sudo systemctl stop {service_name}")
        elif self.system == "Darwin":
            result = self.executor.run(f"launchctl unload -w /Library/LaunchDaemons/{service_name}.plist")
        else:
            result = self.executor.run(f"service {service_name} stop")
        
        success = result["return_code"] == 0
        
        self.logger.log(
            action_type="service",
            action=f"stop_service({service_name})",
            result="Stopped successfully" if success else result["error"],
            success=success,
            error_message=result["error"] if not success else None
        )
        
        return {
            "service_name": service_name,
            "action": "stop",
            "success": success,
            "output": result["output"],
            "error": result["error"] if not success else None
        }
    
    def restart_service(self, service_name: str) -> Dict[str, Any]:
        """
        Restart a service (stop then start)
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dict with execution result
        """
        # Check status first
        status_before = self.check_service(service_name)
        
        # Stop the service
        stop_result = self.stop_service(service_name)
        if not stop_result["success"] and status_before["is_running"]:
            # If it was running and stop failed, return error
            return {
                "service_name": service_name,
                "action": "restart",
                "success": False,
                "error": f"Failed to stop service: {stop_result.get('error', 'Unknown error')}",
                "output": ""
            }
        
        # Start the service
        start_result = self.start_service(service_name)
        
        # Verify it's running
        status_after = self.check_service(service_name)
        
        success = start_result["success"] and status_after["is_running"]
        
        self.logger.log(
            action_type="service",
            action=f"restart_service({service_name})",
            result="Restarted successfully" if success else "Restart failed",
            success=success,
            metadata={
                "status_before": status_before["status"],
                "status_after": status_after["status"]
            }
        )
        
        return {
            "service_name": service_name,
            "action": "restart",
            "success": success,
            "status_before": status_before["status"],
            "status_after": status_after["status"],
            "output": start_result.get("output", ""),
            "error": start_result.get("error") if not success else None
        }
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """
        Get detailed status of a service (alias for check_service with more info)
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dict with detailed status information
        """
        return self.check_service(service_name)

