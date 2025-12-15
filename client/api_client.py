"""
API Client - HTTP client for Command Center
"""

import requests
from typing import Dict, Any, Optional
from .config import Config


class CommandCenterClient:
    """
    HTTP client for Command Center API
    Uses persistent session to maintain cookies (for state persistence)
    """
    
    def __init__(self, api_url: Optional[str] = None, timeout: int = 30, config: Optional[Config] = None):
        """
        Initialize API client
        
        Args:
            api_url: Command Center API URL (defaults to config)
            timeout: Request timeout in seconds
            config: Config instance (creates new if not provided)
        """
        self.config = config or Config()
        self.api_url = api_url or self.config.get_api_url()
        self.timeout = timeout or self.config.get_timeout()
        # Use persistent session to maintain cookies across requests
        self.session = requests.Session()
    
    def execute(
        self,
        request: str,
        use_llm: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Execute a request via Command Center API
        
        Args:
            request: User's request string
            use_llm: Whether to use LLM (Phase 3) or hardcoded (Phase 2)
                     If None, uses config default
            
        Returns:
            Dict with API response
            
        Raises:
            requests.RequestException: If API request fails
        """
        if use_llm is None:
            use_llm = self.config.get_default_use_llm()
        
        url = f"{self.api_url}/api/execute"
        
        payload = {
            "request": request,
            "use_llm": use_llm
        }
        
        try:
            # Use session to maintain cookies (for state persistence)
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": f"Could not connect to Command Center at {self.api_url}. Is the server running?",
                "data": {},
                "original_request": request,
                "error": "connection_error"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": f"Request timed out after {self.timeout} seconds",
                "data": {},
                "original_request": request,
                "error": "timeout"
            }
        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "message": f"HTTP error: {e.response.status_code} - {e.response.text}",
                "data": {},
                "original_request": request,
                "error": "http_error"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "data": {},
                "original_request": request,
                "error": "unknown_error"
            }
    
    def get_supported_actions(self) -> Dict[str, Any]:
        """Get supported actions from API (Phase 2)"""
        try:
            response = self.session.get(
                f"{self.api_url}/api/supported-actions",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_tools(self) -> Dict[str, Any]:
        """Get available tools from API (Phase 3)"""
        try:
            response = self.session.get(
                f"{self.api_url}/api/tools",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """Check if API server is reachable"""
        try:
            response = self.session.get(
                f"{self.api_url}/",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

