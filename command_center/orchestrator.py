"""
Action Orchestrator - Execute action plans step by step
"""

from typing import List, Dict, Any, Optional

from action_agent import CommandExecutor, ServiceManager


class ActionOrchestrator:
    """
    Executes action plans step by step
    Calls Action Agent functions based on plan steps
    """
    
    def __init__(
        self,
        executor: Optional[CommandExecutor] = None,
        service_manager: Optional[ServiceManager] = None
    ):
        """
        Initialize orchestrator
        
        Args:
            executor: CommandExecutor instance
            service_manager: ServiceManager instance
        """
        self.executor = executor or CommandExecutor()
        self.service_manager = service_manager or ServiceManager(executor=self.executor)
        
        # Map function names to actual functions
        self.function_map = {
            "run_command": self._run_command,
            "check_service": self._check_service,
            "start_service": self._start_service,
            "stop_service": self._stop_service,
            "restart_service": self._restart_service,
            "list_services": self._list_services,
        }
    
    def execute_plan(self, plan: List[Dict[str, Any]], fail_fast: bool = True) -> Dict[str, Any]:
        """
        Execute an action plan step by step
        
        Args:
            plan: List of action steps
            fail_fast: If True, stop on first error; if False, continue
            
        Returns:
            Dict with:
                - success: bool
                - steps: List of step results
                - final_result: Final result
                - errors: List of errors
        """
        if not plan:
            return {
                "success": False,
                "steps": [],
                "final_result": None,
                "errors": ["Empty action plan"],
                "message": "No action plan provided"
            }
        
        steps = []
        errors = []
        
        for i, step in enumerate(plan):
            step_name = step.get("step", f"step_{i}")
            function_name = step.get("function")
            args = step.get("args", [])
            
            if function_name not in self.function_map:
                error_msg = f"Unknown function: {function_name}"
                errors.append(error_msg)
                steps.append({
                    "step": step_name,
                    "function": function_name,
                    "success": False,
                    "error": error_msg
                })
                if fail_fast:
                    break
                continue
            
            # Execute the function
            try:
                func = self.function_map[function_name]
                result = func(*args)
                
                step_result = {
                    "step": step_name,
                    "function": function_name,
                    "success": result.get("success", False) if isinstance(result, dict) else bool(result),
                    "result": result
                }
                
                steps.append(step_result)
                
                # Check if step failed
                if not step_result["success"]:
                    error_msg = result.get("error", "Step failed") if isinstance(result, dict) else "Step failed"
                    errors.append(f"{step_name}: {error_msg}")
                    if fail_fast:
                        break
                        
            except Exception as e:
                error_msg = str(e)
                errors.append(f"{step_name}: {error_msg}")
                steps.append({
                    "step": step_name,
                    "function": function_name,
                    "success": False,
                    "error": error_msg
                })
                if fail_fast:
                    break
        
        # Determine overall success
        success = len(errors) == 0 and all(step.get("success", False) for step in steps)
        final_result = steps[-1]["result"] if steps else None
        
        return {
            "success": success,
            "steps": steps,
            "final_result": final_result,
            "errors": errors,
            "steps_count": len(steps)
        }
    
    # Action Agent function wrappers
    def _run_command(self, command: str) -> Dict[str, Any]:
        """Wrapper for run_command"""
        return self.executor.run(command)
    
    def _check_service(self, service_name: str) -> Dict[str, Any]:
        """Wrapper for check_service"""
        return self.service_manager.check_service(service_name)
    
    def _start_service(self, service_name: str) -> Dict[str, Any]:
        """Wrapper for start_service"""
        return self.service_manager.start_service(service_name)
    
    def _stop_service(self, service_name: str) -> Dict[str, Any]:
        """Wrapper for stop_service"""
        return self.service_manager.stop_service(service_name)
    
    def _restart_service(self, service_name: str) -> Dict[str, Any]:
        """Wrapper for restart_service"""
        return self.service_manager.restart_service(service_name)
    
    def _list_services(self) -> Dict[str, Any]:
        """List services (placeholder - can be expanded)"""
        # Simple implementation - can be expanded
        result = self.executor.run("systemctl list-units --type=service --state=running 2>/dev/null || ps aux | head -10")
        return {
            "success": True,
            "output": result.get("output", ""),
            "services": []  # Can parse and extract service names
        }

