"""
LLM Client - Integration with OpenAI/Anthropic APIs
Handles LLM communication for function calling
"""

import os
from typing import List, Dict, Any, Optional
from openai import OpenAI


class LLMClient:
    """
    Client for OpenAI API with function calling support
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None
    ):
        """
        Initialize LLM client
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (default: gpt-4o-mini)
            base_url: Custom base URL (for Azure OpenAI or other providers)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model
        
        # Initialize OpenAI client with 30 minute timeout
        client_kwargs = {
            "api_key": self.api_key,
            "timeout": 1800.0  # 30 minutes (1800 seconds)
        }
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = OpenAI(**client_kwargs)
    
    def chat_with_functions(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        function_call: str = "auto"
    ) -> Dict[str, Any]:
        """
        Send chat request with function calling support
        
        Args:
            messages: List of message dicts (role, content)
            functions: List of function definitions (OpenAI function calling format)
            function_call: "auto", "none", or function name
            
        Returns:
            Dict with response from LLM, including function calls if any
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=[{"type": "function", "function": func} for func in functions] if functions else None,
                tool_choice=function_call if functions else None,
                temperature=0.3  # Lower temperature for more deterministic function calling
            )
            
            message = response.choices[0].message
            
            # Check if LLM wants to call a function
            tool_calls = message.tool_calls if hasattr(message, 'tool_calls') and message.tool_calls else []
            
            result = {
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",  # Required by OpenAI API
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in tool_calls
                ] if tool_calls else [],
                "role": message.role
            }
            
            return result
            
        except Exception as e:
            return {
                "content": None,
                "tool_calls": [],
                "error": str(e),
                "role": "assistant"
            }
    
    def get_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Simple text completion (no function calling)
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Completion text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

