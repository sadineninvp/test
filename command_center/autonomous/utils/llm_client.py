"""
LLM Client utility for autonomous agent
Reuses existing LLMClient from command_center
"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI


def get_llm_client(
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.3
) -> ChatOpenAI:
    """
    Get LangChain ChatOpenAI client
    
    Args:
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        model: Model name
        temperature: Temperature setting
        
    Returns:
        ChatOpenAI instance
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    return ChatOpenAI(
        api_key=api_key,
        model=model,
        temperature=temperature,
        timeout=1800.0  # 30 minutes
    )

